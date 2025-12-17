"""
Embedding service.
Pinecone integration for semantic search.
"""

from app.embedder import get_embedding_service as _get_embedding_service

# Re-export for service layer
get_embedding_service = _get_embedding_service
