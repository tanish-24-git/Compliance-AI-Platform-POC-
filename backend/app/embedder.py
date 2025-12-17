"""
Embedding generation and Pinecone vector store integration.
Uses llama-text-embed-v2 model for 1024-dimensional embeddings.
"""

import os
import logging
from typing import List, Dict, Optional
from pinecone import Pinecone, ServerlessSpec
import requests

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generate embeddings and manage Pinecone vector store"""

    def __init__(self):
        """Initialize Pinecone client and validate configuration"""
        self.api_key = self._validate_env("PINECONE_API_KEY")
        self.index_name = os.getenv("PINECONE_INDEX", "poc")
        self.environment = os.getenv("PINECONE_ENV", "us-east-1")
        self.dimension = int(os.getenv("EMBEDDING_DIMENSIONS", "1024"))
        self.metric = os.getenv("EMBEDDING_METRIC", "cosine")
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.api_key)
        self.index = None
        
        try:
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")
        except Exception as e:
            logger.error(f"Failed to connect to Pinecone index: {e}")
            raise ValueError(
                f"Pinecone index '{self.index_name}' not found. "
                f"Please create the index manually with {self.dimension} dimensions "
                f"and {self.metric} metric."
            )

    @staticmethod
    def _validate_env(var_name: str) -> str:
        """Validate required environment variable"""
        value = os.getenv(var_name)
        if not value:
            raise ValueError(f"{var_name} environment variable is required")
        return value

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using Groq's llama-text-embed-v2.
        
        Note: Since llama-text-embed-v2 is not directly available via Groq API,
        we'll use a simple approach with Groq's API for now.
        In production, you'd use the actual embedding model endpoint.
        """
        try:
            # For this POC, we'll use a simple embedding approach
            # In production, replace with actual llama-text-embed-v2 API call
            from groq import Groq
            
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                raise ValueError("GROQ_API_KEY required for embeddings")
            
            # Note: This is a placeholder. Groq doesn't expose embedding endpoints yet.
            # For production, use a proper embedding service or model
            # For now, we'll create a simple hash-based embedding for demo purposes
            import hashlib
            import numpy as np
            
            # Create deterministic embedding from text hash
            text_hash = hashlib.sha256(text.encode()).digest()
            # Convert to 1024-dim vector
            embedding = np.frombuffer(text_hash * 32, dtype=np.float32)[:1024]
            # Normalize
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding.tolist()
        
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    def store_rule_embedding(self, rule_id: int, rule_text: str) -> bool:
        """
        Store rule embedding in Pinecone for semantic search.
        
        Args:
            rule_id: Database ID of the rule
            rule_text: Text of the rule
        
        Returns:
            True if successful
        """
        try:
            embedding = self.generate_embedding(rule_text)
            
            self.index.upsert(
                vectors=[{
                    "id": f"rule_{rule_id}",
                    "values": embedding,
                    "metadata": {
                        "rule_id": rule_id,
                        "rule_text": rule_text[:500],  # Store truncated text
                        "type": "rule"
                    }
                }]
            )
            
            logger.info(f"Stored embedding for rule {rule_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to store rule embedding: {e}")
            return False

    def find_similar_rules(self, text: str, top_k: int = 5, 
                          similarity_threshold: float = 0.85) -> List[Dict]:
        """
        Find similar rules using semantic search.
        Used for duplicate detection.
        
        Args:
            text: Text to search for
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score
        
        Returns:
            List of similar rules with scores
        """
        try:
            embedding = self.generate_embedding(text)
            
            results = self.index.query(
                vector=embedding,
                top_k=top_k,
                include_metadata=True,
                filter={"type": "rule"}
            )
            
            similar_rules = []
            for match in results.matches:
                if match.score >= similarity_threshold:
                    similar_rules.append({
                        "rule_id": match.metadata.get("rule_id"),
                        "rule_text": match.metadata.get("rule_text"),
                        "similarity_score": match.score
                    })
            
            logger.info(f"Found {len(similar_rules)} similar rules")
            return similar_rules
        
        except Exception as e:
            logger.error(f"Failed to search similar rules: {e}")
            return []

    def delete_rule_embedding(self, rule_id: int) -> bool:
        """Delete rule embedding from Pinecone"""
        try:
            self.index.delete(ids=[f"rule_{rule_id}"])
            logger.info(f"Deleted embedding for rule {rule_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete rule embedding: {e}")
            return False


# Singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service singleton"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
