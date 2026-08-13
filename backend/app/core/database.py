from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

# SQLite database connection setup
engine = create_engine(
    settings.DATABASE_URL, 
    echo=True,  # Dev debugging: Terminal par generated SQL queries print honge
    connect_args={"check_same_thread": False} # SQLite multithreading support
)

def create_db_and_tables():
    """
    FastAPI startup event par database `.db` file aur saare SQL tables generate karega.
    """
    SQLModel.metadata.create_all(engine)

def get_session():
    """
    API Endpoints ke liye database session generator.
    """
    with Session(engine) as session:
        yield session