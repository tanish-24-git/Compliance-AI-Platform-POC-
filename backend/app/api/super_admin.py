from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.rule import (
    RuleCreate,
    RuleUpdate,
    RuleResponse,
    DuplicateCheckRequest,
    DuplicateCheckResponse,
    DuplicateMatch
)
from app.services.rule_service import RuleService
from app.services.duplicate_detector import DuplicateDetector
from app.providers.gemini_provider import GeminiProvider
from app.providers.groq_provider import GroqProvider
from app.providers.pinecone_provider import PineconeProvider
from app.core.config import settings
from typing import List
from uuid import UUID

router = APIRouter(prefix="/super-admin", tags=["Super Admin"])


def get_rule_service(db: Session = Depends(get_db)) -> RuleService:
    """Dependency for rule service"""
    llm_provider = GeminiProvider() if settings.DEFAULT_LLM_PROVIDER == "gemini" else GroqProvider()
    vector_provider = PineconeProvider()
    return RuleService(db=db, llm_provider=llm_provider, vector_provider=vector_provider)


def get_duplicate_detector(db: Session = Depends(get_db)) -> DuplicateDetector:
    """Dependency for duplicate detector"""
    llm_provider = GeminiProvider() if settings.DEFAULT_LLM_PROVIDER == "gemini" else GroqProvider()
    vector_provider = PineconeProvider()
    return DuplicateDetector(db=db, llm_provider=llm_provider, vector_provider=vector_provider)


@router.post("/rules", response_model=RuleResponse)
async def create_rule(
    rule: RuleCreate,
    created_by: str,
    service: RuleService = Depends(get_rule_service)
):
    """Create a new rule manually"""
    try:
        created_rule = await service.create_rule(
            rule_text=rule.rule_text,
            category=rule.category,
            severity=rule.severity,
            created_by=UUID(created_by)
        )
        return created_rule
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rules/extract")
async def extract_rules_from_pdf(
    created_by: str,
    file: UploadFile = File(...),
    service: RuleService = Depends(get_rule_service)
):
    """Upload PDF and extract rules"""
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file content
        file_content = await file.read()
        
        # Extract rules
        extracted_rules = await service.extract_rules_from_pdf(
            pdf_content=file_content,
            created_by=UUID(created_by)
        )
        
        return {
            "message": f"Extracted {len(extracted_rules)} rules",
            "rules": [RuleResponse.model_validate(r) for r in extracted_rules]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules", response_model=List[RuleResponse])
async def list_rules(
    db: Session = Depends(get_db),
    include_inactive: bool = False
):
    """List all rules with versions"""
    try:
        from app.models.rule import Rule
        
        query = db.query(Rule)
        if not include_inactive:
            query = query.filter(Rule.is_active == True)
        
        rules = query.order_by(Rule.created_at.desc()).all()
        return rules
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/rules/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: UUID,
    rule_update: RuleUpdate,
    updated_by: str,
    service: RuleService = Depends(get_rule_service)
):
    """Update rule (creates new version)"""
    try:
        updated_rule = await service.update_rule(
            rule_id=rule_id,
            updated_by=UUID(updated_by),
            rule_text=rule_update.rule_text,
            category=rule_update.category,
            severity=rule_update.severity
        )
        return updated_rule
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rules/{rule_id}/activate")
async def activate_rule(
    rule_id: UUID,
    actor_id: str,
    service: RuleService = Depends(get_rule_service)
):
    """Activate a rule"""
    try:
        rule = service.activate_rule(rule_id, UUID(actor_id))
        return {"message": "Rule activated", "rule": RuleResponse.model_validate(rule)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rules/{rule_id}/deactivate")
async def deactivate_rule(
    rule_id: UUID,
    actor_id: str,
    service: RuleService = Depends(get_rule_service)
):
    """Deactivate a rule"""
    try:
        rule = service.deactivate_rule(rule_id, UUID(actor_id))
        return {"message": "Rule deactivated", "rule": RuleResponse.model_validate(rule)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rules/check-duplicate", response_model=DuplicateCheckResponse)
async def check_duplicate(
    request: DuplicateCheckRequest,
    detector: DuplicateDetector = Depends(get_duplicate_detector)
):
    """Check for duplicate rules before creation"""
    try:
        result = await detector.check_duplicates(request.rule_text)
        
        matches = [
            DuplicateMatch(
                rule_id=UUID(m["rule_id"]),
                rule_text=m["rule_text"],
                similarity_score=m["similarity_score"],
                match_type=m["match_type"]
            )
            for m in result["matches"]
        ]
        
        return DuplicateCheckResponse(
            is_duplicate=result["is_duplicate"],
            matches=matches
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
