from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Repository(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    repo_name: str = Field(index=True) # e.g. "Akshit-Dixit/redshield-ai"
    owner: str
    github_repo_id: int = Field(unique=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)