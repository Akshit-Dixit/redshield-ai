import asyncio
import httpx
from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request, status, Depends
from pydantic import BaseModel
from typing import Optional
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.repository import Repository
from app.models.test_run import TestRun
from app.models.test_result import TestResult
from app.engine.vectors import get_attack_vectors
from app.engine.evaluator import evaluate_response
from app.services.github_service import GitHubService

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

class GitHubRepositoryOwner(BaseModel):
    login: str

class GitHubRepositoryPayload(BaseModel):
    id: int
    full_name: str
    owner: GitHubRepositoryOwner

class GitHubWebhookPayload(BaseModel):
    after: str
    repository: GitHubRepositoryPayload

async def process_redteaming_run(test_run_id: int, commit_sha: str, repo_owner: str, repo_name: str, session: Session):
    github_service = GitHubService()
    
    # 1. Post 'pending' status check to GitHub Commit
    await github_service.update_commit_status(
        owner=repo_owner,
        repo=repo_name,
        sha=commit_sha,
        state="pending",
        description="RedShield AI security evaluation in progress..."
    )

    # Dynamic target chatbot endpoint (Mock target or external RAG chatbot API)
    target_api_url = "http://127.0.0.1:8000/api/v1/mock-target/chat"
    
    vectors = get_attack_vectors()
    total_risk = 0.0
    vulnerable_count = 0

    async with httpx.AsyncClient() as client:
        for vector in vectors:
            # Send live attack prompt to target chatbot API
            try:
                target_resp = await client.post(
                    target_api_url, 
                    json={"prompt": vector["prompt"]}, 
                    timeout=5.0
                )
                model_response = target_resp.json().get("response", "")
            except Exception as e:
                model_response = f"Target service error: {str(e)}"

            eval_res = await evaluate_response(vector, model_response)
            if eval_res["is_vulnerable"]:
                vulnerable_count += 1
                total_risk += eval_res["risk_score"]

            result = TestResult(
                test_run_id=test_run_id,
                category=vector["category"],
                attack_prompt=vector["prompt"],
                model_response=model_response,
                is_vulnerable=eval_res["is_vulnerable"],
                judge_reasoning=eval_res["reasoning"]
            )
            session.add(result)

    test_run = session.get(TestRun, test_run_id)
    if test_run:
        avg_risk = (total_risk / len(vectors)) if len(vectors) > 0 else 0.0
        risk_score = round(avg_risk, 2)
        test_run.risk_score = risk_score
        test_run.status = "PASSED" if vulnerable_count == 0 else "FAILED"
        session.add(test_run)
        session.commit()

        # 2. Post final Pass/Fail status check back to GitHub Commit
        if vulnerable_count == 0:
            await github_service.update_commit_status(
                owner=repo_owner,
                repo=repo_name,
                sha=commit_sha,
                state="success",
                description=f"Passed Security Guardrails. Risk Score: {risk_score}%"
            )
        else:
            await github_service.update_commit_status(
                owner=repo_owner,
                repo=repo_name,
                sha=commit_sha,
                state="failure",
                description=f"Failed Security Check! {vulnerable_count} Vulnerabilities Detected. Risk Score: {risk_score}%"
            )

@router.post("/github", status_code=status.HTTP_202_ACCEPTED)
async def handle_github_webhook(
    payload: GitHubWebhookPayload,
    background_tasks: BackgroundTasks,
    x_github_event: Optional[str] = Header(None),
    session: Session = Depends(get_session)
):
    if x_github_event and x_github_event != "push":
        return {"message": f"Event '{x_github_event}' ignored. Only push events are processed."}

    commit_sha = payload.after
    full_repo_name = payload.repository.full_name
    repo_owner = payload.repository.owner.login
    repo_name_only = full_repo_name.split("/")[-1] if "/" in full_repo_name else full_repo_name

    statement = select(Repository).where(Repository.repo_name == full_repo_name)
    repo = session.exec(statement).first()
    
    if not repo:
        repo = Repository(
            repo_name=full_repo_name,
            owner=repo_owner,
            github_repo_id=payload.repository.id
        )
        session.add(repo)
        session.commit()
        session.refresh(repo)

    test_run = TestRun(
        repository_id=repo.id,
        commit_sha=commit_sha,
        status="PENDING",
        risk_score=0.0
    )
    session.add(test_run)
    session.commit()
    session.refresh(test_run)

    # Queue async background runner
    background_tasks.add_task(process_redteaming_run, test_run.id, commit_sha, repo_owner, repo_name_only, session)

    return {
        "status": "accepted",
        "message": "Webhook received. RedShield AI evaluation pipeline queued.",
        "test_run_id": test_run.id,
        "run_status": "PENDING"
    }