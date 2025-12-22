from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@postgres:5432/compliance_db"
    
    # LLM Providers
    GEMINI_API_KEY: str
    GROQ_API_KEY: str
    
    # Pinecone Configuration
    PINECONE_API_KEY: str
    PINECONE_ENV: str = "us-east-1"
    PINECONE_INDEX: str = "poc"
    PINECONE_HOST: str
    
    # Embedding Configuration
    EMBEDDING_MODEL: str = "llama-text-embed-v2"
    EMBEDDING_DIMENSIONS: int = 1024
    EMBEDDING_METRIC: str = "cosine"
    
    # LLM Selection
    DEFAULT_LLM_PROVIDER: str = "groq"  # gemini or groq
    REVIEWER_LLM_PROVIDER: str = "groq"
    
    # Duplicate Detection
    SEMANTIC_SIMILARITY_THRESHOLD: float = 0.95
    
    # Application
    APP_NAME: str = "Compliance AI POC"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
