# Compliance Service Documentation

## Overview
The `ComplianceService` (`backend/app/services/compliance_service.py`) handles the validation of existing documents (PDF, DOCX, TXT). It breaks down documents into analyzable chunks, checks them against active compliance rules, and creates a comprehensive compliance report.

## Key Responsibilities
- **Document Extraction**: Parses text from PDF, DOCX, and text files, preserving metadata like page numbers and section headers.
- **Token-Based Chunking**: Splits large documents into manageable chunks based on token count to fit LLM context windows, ensuring overlap for context preservation.
- **Compliance Checking**: Validates each chunk against active rules using deterministic keyword matching (and optionally LLM-based checks).
- **Rewriting**: Provides functionality to rewrite non-compliant text sections.

## Core Functions

### `check_document_compliance`
**Signature**: `async def check_document_compliance(self, file_content: bytes, filename: str, user_id: UUID) -> Dict`
- Main entry point for document uploads.
- extracting text -> chunking -> checking -> reporting.

### `rewrite_compliant`
**Signature**: `async def rewrite_compliant(self, violating_text: str, violated_rules: List[Dict]) -> str`
- Uses the LLM to rewrite a specific block of text to resolve identified violations.

### Internal Methods
- `_extract_document_text`: Router for PDF/DOCX parsers.
- `_chunk_by_tokens`: Sophisticated chunking logic using `tiktoken`.
- `_check_chunk_compliance`: Iterates through rules to check a specific text chunk.
- `_check_rule_violation`: Logic to check if text violates a specific rule (e.g., negative keyword "guarantee").

## Workflow Diagram

```mermaid
flowchart TD
    A[Upload Document] --> B{File Type?}
    B -->|PDF| C[Extract PDF Text + Metadata]
    B -->|DOCX| D[Extract DOCX Text]
    B -->|TXT| E[Read Text]
    
    C & D & E --> F[Token-Based Chunking]
    F --> G[Load Active Rules]
    
    subgraph Analysis Loop [For Each Chunk]
        H[Check Rules]
        I{Violation Found?}
        I -->|Yes| J[Record Violation & Metadata]
        I -->|No| K[Continue]
    end
    
    Analysis Loop --> L[Aggregate Results]
    L --> M[Determine Overall Status]
    M --> N[Save Submission to DB]
    N --> O[Audit Log]
    O --> P[Return Report]
```
