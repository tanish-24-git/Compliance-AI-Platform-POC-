"""
Database configuration and session management.
Moved from app/db.py to app/core/database.py for better organization.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from app.models.models import Base

logger = logging.getLogger(__name__)


def validate_database_url() -> str:
    """
    Validate that DATABASE_URL is set in environment.
    Raises ValueError if missing.
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError(
            "DATABASE_URL environment variable is required. "
            "Please set it in your .env file."
        )
    return database_url


# Create engine with connection pooling
DATABASE_URL = validate_database_url()
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database by creating all tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI endpoints to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """Get a database session for use outside of FastAPI dependency injection."""
    return SessionLocal()
