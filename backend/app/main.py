from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI App Instance
app = FastAPI(
    title="RedShield AI Engine",
    description="AutomatedLM R Led-Teaming CI/CD Pipeline Engine",
    version="1.0.0"
)

# Configure Cross-Origin Resource Sharing (CORS)
# Allows our React frontend (running on a different port) to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin in dev mode
    allow_credentials=True,
    allow_methods=["*"],  # Allows GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],
)

# Health Check Endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify if backend server is up and running.
    """
    return {
        "status": "healthy",
        "service": "RedShield AI Backend Engine",
        "version": "1.0.0"
    }