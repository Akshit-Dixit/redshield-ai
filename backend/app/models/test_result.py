from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class TestResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    test_run_id: int = Field(foreign_key="testrun.id")
    category: str # e.g. "Prompt Injection", "PII Leakage", "Jailbreak"
    attack_prompt: str
    model_response: str
    is_vulnerable: bool = Field(default=False)
    judge_reasoning: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)