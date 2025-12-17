"""
Document parser for PDF, DOCX, and Markdown files.
Preserves structure and legal language without loss.
"""

import logging
from pathlib import Path
from typing import Optional
import PyPDF2
from docx import Document
import markdown

logger = logging.getLogger(__name__)


class DocumentParser:
    """Parse various document formats while preserving structure"""

    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """
        Extract text from PDF file.
        Preserves page breaks and structure.
        """
        try:
            text_content = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text.strip():
                        text_content.append(f"--- Page {page_num + 1} ---\n{text}")
                
            result = "\n\n".join(text_content)
            logger.info(f"Successfully parsed PDF: {file_path} ({num_pages} pages)")
            return result
        
        except Exception as e:
            logger.error(f"Failed to parse PDF {file_path}: {e}")
            raise ValueError(f"PDF parsing failed: {str(e)}")

    @staticmethod
    def parse_docx(file_path: str) -> str:
        """
        Extract text from DOCX file.
        Preserves paragraph structure.
        """
        try:
            doc = Document(file_path)
            paragraphs = []
            
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    paragraphs.append(text)
            
            result = "\n\n".join(paragraphs)
            logger.info(f"Successfully parsed DOCX: {file_path} ({len(paragraphs)} paragraphs)")
            return result
        
        except Exception as e:
            logger.error(f"Failed to parse DOCX {file_path}: {e}")
            raise ValueError(f"DOCX parsing failed: {str(e)}")

    @staticmethod
    def parse_markdown(file_path: str) -> str:
        """
        Extract text from Markdown file.
        Converts to plain text while preserving structure.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                md_content = file.read()
            
            # Convert markdown to HTML, then strip HTML tags for plain text
            # This preserves the semantic structure
            html = markdown.markdown(md_content)
            
            # For compliance checking, we want the raw markdown
            # as it contains the actual legal language
            logger.info(f"Successfully parsed Markdown: {file_path}")
            return md_content
        
        except Exception as e:
            logger.error(f"Failed to parse Markdown {file_path}: {e}")
            raise ValueError(f"Markdown parsing failed: {str(e)}")

    @classmethod
    def parse_file(cls, file_path: str, file_type: Optional[str] = None) -> str:
        """
        Parse file based on extension or provided file type.
        
        Args:
            file_path: Path to the file
            file_type: Optional file type override (pdf, docx, md)
        
        Returns:
            Extracted text content
        
        Raises:
            ValueError: If file type is unsupported or parsing fails
        """
        path = Path(file_path)
        
        # Determine file type
        if file_type:
            ext = file_type.lower()
        else:
            ext = path.suffix.lower().lstrip('.')
        
        # Route to appropriate parser
        if ext == 'pdf':
            return cls.parse_pdf(file_path)
        elif ext in ['docx', 'doc']:
            return cls.parse_docx(file_path)
        elif ext in ['md', 'markdown']:
            return cls.parse_markdown(file_path)
        else:
            raise ValueError(
                f"Unsupported file type: {ext}. "
                f"Supported types: pdf, docx, md"
            )


def parse_document(file_path: str, file_type: Optional[str] = None) -> str:
    """
    Convenience function to parse a document.
    
    Args:
        file_path: Path to the document
        file_type: Optional file type (pdf, docx, md)
    
    Returns:
        Extracted text content
    """
    parser = DocumentParser()
    return parser.parse_file(file_path, file_type)
