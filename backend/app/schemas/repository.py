from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Input Schema (Jab user frontend ya webhook se repo register karega)
class RepositoryCreate(BaseModel):
    repo_name: str # e.g., "Akshit-Dixit/redshield-ai"
    owner: str
    github_repo_id: int

# Response Schema (Jab API response bhejegi)
class RepositoryRead(BaseModel):
    id: int
    repo_name: str
    owner: str
    github_repo_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True