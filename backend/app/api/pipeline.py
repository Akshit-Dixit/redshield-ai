from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.core.database import get_session
from app.models.test_run import TestRun
from app.models.test_result import TestResult
from app.engine.vectors import get_attack_vectors
from app.engine.evaluator import evaluate_response
from pydantic import BaseModel

router = APIRouter(prefix="/pipeline", tags=["Red-Teaming Pipeline"])

class TriggerPipelineRequest(BaseModel):
    repository_id: int
    commit_sha: str
    target_chat_response: str  # Simulated response from target LLM for testing

@router.post("/run")
def trigger_redteaming_pipeline(
    payload: TriggerPipelineRequest,
    session: Session = Depends(get_session)
):
    """
    Executes automated red-teaming vectors against target response and persists logs.
    """
    # 1. Create a TestRun entry
    test_run = TestRun(
        repository_id=payload.repository_id,
        commit_sha=payload.commit_sha,
        status="running",
        risk_score=0.0
    )
    session.add(test_run)
    session.commit()
    session.refresh(test_run)

    vectors = get_attack_vectors()
    total_risk = 0.0
    vulnerable_count = 0

    # 2. Iterate vectors & evaluate target response
    for vector in vectors:
        eval_res = evaluate_response(vector, payload.target_chat_response)
        if eval_res["is_vulnerable"]:
            vulnerable_count += 1
            total_risk += eval_res["risk_score"]

        # Persist TestResult log
        result = TestResult(
            test_run_id=test_run.id,
            category=vector["category"],
            attack_prompt=vector["prompt"],
            model_response=payload.target_chat_response,
            is_vulnerable=eval_res["is_vulnerable"],
            judge_reasoning=eval_res["reasoning"]
        )
        session.add(result)

    # 3. Update overall TestRun score & status
    avg_risk = (total_risk / len(vectors)) if len(vectors) > 0 else 0.0
    test_run.risk_score = round(avg_risk, 2)
    test_run.status = "completed"
    session.add(test_run)
    session.commit()

    return {
        "test_run_id": test_run.id,
        "status": test_run.status,
        "overall_risk_score": test_run.risk_score,
        "vulnerabilities_detected": vulnerable_count
    }