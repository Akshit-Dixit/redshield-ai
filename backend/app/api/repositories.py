from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.core.database import get_session
from app.models.repository import Repository
from app.schemas.repository import RepositoryCreate, RepositoryRead

router = APIRouter(prefix="/repositories", tags=["Repositories"])

@router.post("/", response_model=RepositoryRead, status_code=status.HTTP_201_CREATED)
def register_repository(
    repo_data: RepositoryCreate,
    session: Session = Depends(get_session)
):
    """
    Register a new GitHub Repository for RedShield monitoring.
    """
    # Check if repository already exists
    statement = select(Repository).where(Repository.github_repo_id == repo_data.github_repo_id)
    existing_repo = session.exec(statement).first()
    if existing_repo:
        raise HTTPException(
            status_code=400, 
            detail="Repository with this GitHub Repo ID is already registered."
        )

    db_repo = Repository(
        repo_name=repo_data.repo_name,
        owner=repo_data.owner,
        github_repo_id=repo_data.github_repo_id
    )
    session.add(db_repo)
    session.commit()
    session.refresh(db_repo)
    return db_repo

@router.get("/", response_model=List[RepositoryRead])
def list_repositories(session: Session = Depends(get_session)):
    """
    Fetch all registered repositories.
    """
    repositories = session.exec(select(Repository)).all()
    return repositories