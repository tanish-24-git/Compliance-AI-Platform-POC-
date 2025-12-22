from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.content import (
    ContentGenerateRequest,
    ContentGenerateResponse,
    DocumentCheckResponse,
    ContentRewriteRequest,
    RuleTriggered
)
from app.services.content_service import ContentService
from app.services.compliance_service import ComplianceService
from app.providers.gemini_provider import GeminiProvider
from app.providers.groq_provider import GroqProvider
from app.providers.pinecone_provider import PineconeProvider
from app.core.config import settings
from uuid import UUID

router = APIRouter(prefix="/agent", tags=["Agent"])


def get_content_service(db: Session = Depends(get_db)) -> ContentService:
    """Dependency for content service"""
    # Select LLM providers based on config
    print(f"DEBUG: DEFAULT_LLM_PROVIDER={settings.DEFAULT_LLM_PROVIDER}")
    if settings.DEFAULT_LLM_PROVIDER == "gemini":
        generator = GeminiProvider()
    else:
        generator = GroqProvider()
    
    if settings.REVIEWER_LLM_PROVIDER == "gemini":
        reviewer = GeminiProvider()
    else:
        reviewer = GroqProvider()
    
    vector_provider = PineconeProvider()
    
    return ContentService(
        db=db,
        generator_llm=generator,
        reviewer_llm=reviewer,
        vector_provider=vector_provider
    )


def get_compliance_service(db: Session = Depends(get_db)) -> ComplianceService:
    """Dependency for compliance service"""
    llm_provider = GeminiProvider() if settings.DEFAULT_LLM_PROVIDER == "gemini" else GroqProvider()
    return ComplianceService(db=db, llm_provider=llm_provider)


@router.post("/generate", response_model=ContentGenerateResponse)
async def generate_content(
    request: ContentGenerateRequest,
    service: ContentService = Depends(get_content_service)
):
    """Generate compliant content from prompt"""
    try:
        result = await service.generate_content(
            prompt=request.prompt,
            user_id=request.user_id,
            use_prompt_enhancer=request.use_prompt_enhancer
        )
        
        submission = result["submission"]
        
        # Format response
        rules_triggered = [
            RuleTriggered(
                rule_id=UUID(r["rule_id"]) if r["rule_id"] != "ai_detected" else UUID("00000000-0000-0000-0000-000000000000"),
                rule_text=r["rule_text"],
                category=r["category"],
                severity=r["severity"],
                status=r["status"]
            )
            for r in result["rules_triggered"]
        ]
        
        return ContentGenerateResponse(
            submission_id=submission.submission_id,
            final_content=submission.final_content,
            compliance_status=submission.compliance_status,
            rules_triggered=rules_triggered,
            created_at=submission.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-document", response_model=DocumentCheckResponse)
async def check_document(
    user_id: str,
    file: UploadFile = File(...),
    service: ComplianceService = Depends(get_compliance_service)
):
    """Upload and check document for compliance"""
    try:
        # Read file content
        file_content = await file.read()
        
        # Check compliance
        result = await service.check_document_compliance(
            file_content=file_content,
            filename=file.filename,
            user_id=UUID(user_id)
        )
        
        return DocumentCheckResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rewrite")
async def rewrite_content(
    request: ContentRewriteRequest,
    service: ComplianceService = Depends(get_compliance_service),
    db: Session = Depends(get_db)
):
    """Rewrite violating content to be compliant"""
    try:
        # Get submission
        from app.models.content import ContentSubmission
        submission = db.query(ContentSubmission).filter(
            ContentSubmission.submission_id == request.submission_id
        ).first()
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # Get violated rules for this text
        violated_rules = [
            r for r in submission.rules_triggered or []
            if r.get("status") == "violated"
        ]
        
        # Rewrite
        compliant_text = await service.rewrite_compliant(
            violating_text=request.violation_text,
            violated_rules=violated_rules
        )
        
        return {"compliant_text": compliant_text}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
