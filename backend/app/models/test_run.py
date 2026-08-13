from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class TestRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    repository_id: int = Field(foreign_key="repository.id")
    commit_sha: str = Field(index=True)
    branch: str = Field(default="main")
    status: str = Field(default="pending") # pending, running, completed, failed
    risk_score: float = Field(default=0.0) # Overall safety risk score (0 to 100)
    created_at: datetime = Field(default_factory=datetime.utcnow)