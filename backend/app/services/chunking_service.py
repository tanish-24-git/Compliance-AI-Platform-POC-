"""
Chunking service.
Token-based content chunking.
"""

from app.chunker import chunk_content as _chunk_content

# Re-export for service layer
chunk_content = _chunk_content
