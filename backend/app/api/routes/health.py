"""Health check routes"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import status
import os
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint with environment validation.
    Returns status of all required services.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("APP_ENV", "unknown"),
        "checks": {}
    }
    
    # Check required environment variables
    required_vars = [
        "GEMINI_API_KEY",
        "GROQ_API_KEY",
        "PINECONE_API_KEY",
        "DATABASE_URL"
    ]
    
    for var in required_vars:
        health_status["checks"][var] = "configured" if os.getenv(var) else "missing"
    
    # Check if any required vars are missing
    if "missing" in health_status["checks"].values():
        health_status["status"] = "unhealthy"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_status
        )
    
    return health_status
