from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import create_db_and_tables
from app.api.repositories import router as repositories_router
from app.api.pipeline import router as pipeline_router
from app.api.webhooks import router as webhooks_router
from app.api.runs import router as runs_router
from app.engine.mock_target import router as mock_target_router

app = FastAPI(
    title="RedShield AI Engine",
    description="Automated LLM Red-Teaming CI/CD Security Pipeline Engine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Register Routers
app.include_router(repositories_router, prefix="/api/v1")
app.include_router(pipeline_router, prefix="/api/v1")
app.include_router(webhooks_router, prefix="/api/v1")
app.include_router(runs_router, prefix="/api/v1")
app.include_router(mock_target_router, prefix="/api/v1")

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "RedShield AI Backend Engine",
        "version": "1.0.0"
    }