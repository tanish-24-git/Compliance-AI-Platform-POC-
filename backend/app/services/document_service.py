"""
Document parsing service.
Handles PDF, DOCX, and Markdown files.
"""

from app.doc_parser import parse_document as _parse_document

# Re-export for service layer
parse_document = _parse_document
