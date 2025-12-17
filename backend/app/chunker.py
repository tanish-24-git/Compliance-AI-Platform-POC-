"""
Token-based chunking with structure preservation.
Uses tiktoken for accurate token counting (300-500 tokens per chunk).
"""

import logging
from typing import List, Dict
import tiktoken

logger = logging.getLogger(__name__)


class TokenChunker:
    """Structure-first, token-based chunking for compliance content"""

    def __init__(self, min_tokens: int = 300, max_tokens: int = 500, model: str = "gpt-3.5-turbo"):
        """
        Initialize chunker with token limits.
        
        Args:
            min_tokens: Minimum tokens per chunk
            max_tokens: Maximum tokens per chunk
            model: Model name for tiktoken encoding
        """
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fallback to cl100k_base encoding if model not found
            self.encoding = tiktoken.get_encoding("cl100k_base")
        
        logger.info(f"TokenChunker initialized: {min_tokens}-{max_tokens} tokens per chunk")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        return len(self.encoding.encode(text))

    def chunk_text(self, text: str, source_type: str = "unknown") -> List[Dict[str, any]]:
        """
        Chunk text into token-based segments with metadata.
        
        Args:
            text: Text to chunk
            source_type: Type of source (prompt, uploaded_file, generated)
        
        Returns:
            List of chunk dictionaries with text, position, token_count, and source_type
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for chunking")
            return []

        # Split by paragraphs first (structure-first approach)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        chunk_position = 0

        for para in paragraphs:
            para_tokens = self.count_tokens(para)
            
            # If single paragraph exceeds max_tokens, split it by sentences
            if para_tokens > self.max_tokens:
                # If we have accumulated content, save it first
                if current_chunk:
                    chunk_text = "\n\n".join(current_chunk)
                    chunks.append({
                        "chunk_text": chunk_text,
                        "chunk_position": chunk_position,
                        "token_count": current_tokens,
                        "source_type": source_type
                    })
                    chunk_position += 1
                    current_chunk = []
                    current_tokens = 0
                
                # Split long paragraph by sentences
                sentences = self._split_by_sentences(para)
                for sentence in sentences:
                    sent_tokens = self.count_tokens(sentence)
                    
                    if current_tokens + sent_tokens > self.max_tokens and current_chunk:
                        # Save current chunk
                        chunk_text = " ".join(current_chunk)
                        chunks.append({
                            "chunk_text": chunk_text,
                            "chunk_position": chunk_position,
                            "token_count": current_tokens,
                            "source_type": source_type
                        })
                        chunk_position += 1
                        current_chunk = []
                        current_tokens = 0
                    
                    current_chunk.append(sentence)
                    current_tokens += sent_tokens
            
            # Normal paragraph processing
            elif current_tokens + para_tokens > self.max_tokens:
                # Save current chunk if it meets minimum
                if current_tokens >= self.min_tokens:
                    chunk_text = "\n\n".join(current_chunk)
                    chunks.append({
                        "chunk_text": chunk_text,
                        "chunk_position": chunk_position,
                        "token_count": current_tokens,
                        "source_type": source_type
                    })
                    chunk_position += 1
                    current_chunk = [para]
                    current_tokens = para_tokens
                else:
                    # Add to current chunk even if it exceeds max slightly
                    current_chunk.append(para)
                    current_tokens += para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        # Add remaining content as final chunk
        if current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            chunks.append({
                "chunk_text": chunk_text,
                "chunk_position": chunk_position,
                "token_count": current_tokens,
                "source_type": source_type
            })

        logger.info(f"Created {len(chunks)} chunks from {source_type} content")
        return chunks

    def _split_by_sentences(self, text: str) -> List[str]:
        """
        Split text by sentences for long paragraphs.
        Simple sentence splitting by common terminators.
        """
        import re
        # Split by sentence terminators while preserving them
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]


def chunk_content(text: str, source_type: str = "unknown", 
                  min_tokens: int = 300, max_tokens: int = 500) -> List[Dict[str, any]]:
    """
    Convenience function to chunk text content.
    
    Args:
        text: Text to chunk
        source_type: Source type for metadata
        min_tokens: Minimum tokens per chunk
        max_tokens: Maximum tokens per chunk
    
    Returns:
        List of chunk dictionaries
    """
    chunker = TokenChunker(min_tokens=min_tokens, max_tokens=max_tokens)
    return chunker.chunk_text(text, source_type)
