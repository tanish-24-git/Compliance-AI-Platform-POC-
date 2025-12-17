"""
FastAPI main application.
Professional industry-standard structure with modular routes.
"""

import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import core modules
from app.core.database import init_db
from app.api import api_router

# Create FastAPI app
app = FastAPI(
    title="Compliance-First AI Content Generation Platform",
    description="Industry-grade POC for regulated fintech/insurance content generation",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

# Serve static frontend files
try:
    app.mount("/", StaticFiles(directory="/app/frontend/dist", html=True), name="frontend")
    logger.info("Frontend static files mounted successfully")
except Exception as e:
    logger.warning(f"Frontend static files not found: {e}")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        logger.info("Initializing database...")
        init_db()
        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
