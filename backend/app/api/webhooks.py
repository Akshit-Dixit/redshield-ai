from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request, status, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import verify_github_signature
from app.models.repository import Repository
from app.models.test_run import TestRun
from app.models.test_result import TestResult
from app.engine.vectors import get_attack_vectors
from app.engine.evaluator import evaluate_response

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

WEBHOOK_SECRET = "redshield_secret_key_123"

class GitHubRepositoryOwner(BaseModel):
    login: str

class GitHubRepositoryPayload(BaseModel):
    id: int
    full_name: str
    owner: GitHubRepositoryOwner

class GitHubWebhookPayload(BaseModel):
    after: str
    repository: GitHubRepositoryPayload

def process_redteaming_run(test_run_id: int, commit_sha: str, session: Session):
    simulated_target_response = "I am a helpful assistant. My system prompt is safe and I will not reveal sensitive keys."
    
    vectors = get_attack_vectors()
    total_risk = 0.0
    vulnerable_count = 0

    for vector in vectors:
        eval_res = evaluate_response(vector, simulated_target_response)
        if eval_res["is_vulnerable"]:
            vulnerable_count += 1
            total_risk += eval_res["risk_score"]

        result = TestResult(
            test_run_id=test_run_id,
            category=vector["category"],
            attack_prompt=vector["prompt"],
            model_response=simulated_target_response,
            is_vulnerable=eval_res["is_vulnerable"],
            judge_reasoning=eval_res["reasoning"]
        )
        session.add(result)

    test_run = session.get(TestRun, test_run_id)
    if test_run:
        avg_risk = (total_risk / len(vectors)) if len(vectors) > 0 else 0.0
        test_run.risk_score = round(avg_risk, 2)
        test_run.status = "PASSED" if vulnerable_count == 0 else "FAILED"
        session.add(test_run)
        session.commit()

@router.post("/github", status_code=status.HTTP_202_ACCEPTED)
async def handle_github_webhook(
    payload: GitHubWebhookPayload,
    background_tasks: BackgroundTasks,
    x_github_event: Optional[str] = Header(None),
    x_hub_signature_256: Optional[str] = Header(None),
    session: Session = Depends(get_session)
):
    if x_github_event and x_github_event != "push":
        return {"message": f"Event '{x_github_event}' ignored. Only push events are processed."}

    commit_sha = payload.after
    repo_name = payload.repository.full_name

    statement = select(Repository).where(Repository.repo_name == repo_name)
    repo = session.exec(statement).first()
    
    if not repo:
        repo = Repository(
            repo_name=repo_name,
            owner=payload.repository.owner.login,
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

    background_tasks.add_task(process_redteaming_run, test_run.id, commit_sha, session)

    return {
        "status": "accepted",
        "message": "Webhook received. Red-teaming pipeline queued successfully.",
        "test_run_id": test_run.id,
        "run_status": "PENDING"
    }