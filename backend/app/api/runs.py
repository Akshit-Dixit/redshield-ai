from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Dict, Any

from app.core.database import get_session
from app.models.test_run import TestRun
from app.models.test_result import TestResult
from app.models.repository import Repository

router = APIRouter(prefix="/runs", tags=["Dashboard Runs"])

@router.get("", response_model=Dict[str, Any])
def get_dashboard_summary_and_runs(session: Session = Depends(get_session)):
    """
    Returns high-level metric analytics and historical test run entries for the UI Dashboard.
    """
    statement = select(TestRun).order_by(TestRun.id.desc())
    runs = session.exec(statement).all()

    total_runs = len(runs)
    passed_runs = sum(1 for r in runs if r.status == "PASSED")
    failed_runs = sum(1 for r in runs if r.status == "FAILED")
    
    pass_rate = round((passed_runs / total_runs * 100), 1) if total_runs > 0 else 100.0
    avg_risk_score = round(sum(r.risk_score for r in runs) / total_runs, 1) if total_runs > 0 else 0.0

    runs_data = []
    for r in runs:
        repo = session.get(Repository, r.repository_id)
        runs_data.append({
            "id": r.id,
            "repository_name": repo.repo_name if repo else "unknown/repo",
            "commit_sha": r.commit_sha,
            "branch": r.branch,
            "status": r.status,
            "risk_score": r.risk_score,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else "N/A"
        })

    return {
        "metrics": {
            "total_runs": total_runs,
            "passed_runs": passed_runs,
            "failed_runs": failed_runs,
            "pass_rate_percentage": pass_rate,
            "average_risk_score": avg_risk_score
        },
        "runs": runs_data
    }

@router.get("/{run_id}", response_model=Dict[str, Any])
def get_run_details(run_id: int, session: Session = Depends(get_session)):
    """
    Fetches detailed attack vector prompts, raw responses, and judge justifications for a specific run.
    """
    run = session.get(TestRun, run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test run with ID {run_id} not found."
        )

    repo = session.get(Repository, run.repository_id)
    
    statement = select(TestResult).where(TestResult.test_run_id == run_id)
    results = session.exec(statement).all()

    attack_logs = []
    for res in results:
        attack_logs.append({
            "id": res.id,
            "category": res.category,
            "attack_prompt": res.attack_prompt,
            "model_response": res.model_response,
            "is_vulnerable": res.is_vulnerable,
            "judge_reasoning": res.judge_reasoning,
            "created_at": res.created_at.strftime("%Y-%m-%d %H:%M:%S") if res.created_at else "N/A"
        })

    return {
        "run_info": {
            "id": run.id,
            "repository_name": repo.repo_name if repo else "unknown/repo",
            "commit_sha": run.commit_sha,
            "branch": run.branch,
            "status": run.status,
            "risk_score": run.risk_score,
            "created_at": run.created_at.strftime("%Y-%m-%d %H:%M:%S") if run.created_at else "N/A"
        },
        "results": attack_logs
    }