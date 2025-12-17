"""
Super Admin routes for HUMAN-ONLY rule management.

GOVERNANCE PRINCIPLE:
- Rules are written ONLY by humans (Super Admin)
- Uploaded documents are ONLY reference material
- AI has ZERO authority in rule creation
- PostgreSQL is the source of truth
- Pinecone stores only derived embeddings
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import shutil

from app.core.database import get_db
from app.models.models import Rule, RuleSeverity, AuditLog
from app.services.embedding_service import get_embedding_service

router = APIRouter()


class RuleCreate(BaseModel):
    """Human-written rule creation request"""
    rule_text: str  # MANDATORY - typed by human
    severity: str  # "hard" or "soft"
    created_by: int
    source_document_reference: Optional[str] = None  # Optional reference to uploaded doc


class RuleUpdate(BaseModel):
    """Human-written rule update request"""
    rule_text: str  # MANDATORY - typed by human


@router.post("/rules")
async def create_rule(rule_data: RuleCreate, db: Session = Depends(get_db)):
    """
    Super Admin endpoint: Create new compliance rule.
    
    HUMAN-ONLY GOVERNANCE:
    - Rule text MUST be manually typed by Super Admin
    - NO AI suggestions or auto-generation
    - Documents are reference only
    - Includes duplicate detection (exact + semantic)
    """
    try:
        # Validate human input
        if not rule_data.rule_text or not rule_data.rule_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Rule text is required and must be manually entered"
            )
        
        # Check for exact duplicate (PostgreSQL - source of truth)
        existing = db.query(Rule).filter(
            Rule.rule_text == rule_data.rule_text,
            Rule.is_active == True
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Exact duplicate rule already exists"
            )
        
        # Check for semantic duplicate (Pinecone - derived data)
        embedding_service = get_embedding_service()
        similar_rules = embedding_service.find_similar_rules(
            rule_data.rule_text,
            top_k=3,
            similarity_threshold=0.85
        )
        
        if similar_rules:
            # Return warning but allow Super Admin to decide
            return {
                "status": "warning",
                "message": "Similar rules found. Review before creating.",
                "similar_rules": similar_rules,
                "action_required": "Review similarities and confirm creation if rule is distinct"
            }
        
        # Create new rule (human-defined)
        severity = RuleSeverity.HARD if rule_data.severity.lower() == "hard" else RuleSeverity.SOFT
        
        new_rule = Rule(
            rule_text=rule_data.rule_text,
            severity=severity,
            is_active=True,
            version=1,
            created_by=rule_data.created_by
        )
        
        db.add(new_rule)
        db.commit()
        db.refresh(new_rule)
        
        # Store embedding in Pinecone (derived data only)
        try:
            embedding_service.store_rule_embedding(new_rule.id, new_rule.rule_text)
        except Exception as e:
            # Log but don't fail - Pinecone is derived data
            import logging
            logging.warning(f"Failed to store embedding for rule {new_rule.id}: {e}")
        
        # Audit log
        audit = AuditLog(
            user_id=rule_data.created_by,
            action="create_rule",
            entity_type="rule",
            entity_id=new_rule.id,
            details=f"Created {severity.value} rule - Human-defined"
        )
        db.add(audit)
        db.commit()
        
        return {
            "status": "success",
            "message": "Rule created successfully",
            "rule": {
                "id": new_rule.id,
                "rule_text": new_rule.rule_text,
                "severity": new_rule.severity.value,
                "version": new_rule.version,
                "is_active": new_rule.is_active,
                "source": "human_created"
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rules/force-create")
async def force_create_rule(rule_data: RuleCreate, db: Session = Depends(get_db)):
    """
    Force create rule after reviewing similarity warnings.
    Super Admin explicitly confirms rule is distinct.
    """
    try:
        # Validate human input
        if not rule_data.rule_text or not rule_data.rule_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Rule text is required and must be manually entered"
            )
        
        # Check exact duplicate only
        existing = db.query(Rule).filter(
            Rule.rule_text == rule_data.rule_text,
            Rule.is_active == True
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Exact duplicate rule already exists"
            )
        
        # Create rule (Super Admin confirmed it's distinct)
        severity = RuleSeverity.HARD if rule_data.severity.lower() == "hard" else RuleSeverity.SOFT
        
        new_rule = Rule(
            rule_text=rule_data.rule_text,
            severity=severity,
            is_active=True,
            version=1,
            created_by=rule_data.created_by
        )
        
        db.add(new_rule)
        db.commit()
        db.refresh(new_rule)
        
        # Store embedding
        embedding_service = get_embedding_service()
        try:
            embedding_service.store_rule_embedding(new_rule.id, new_rule.rule_text)
        except Exception as e:
            import logging
            logging.warning(f"Failed to store embedding: {e}")
        
        # Audit log
        audit = AuditLog(
            user_id=rule_data.created_by,
            action="force_create_rule",
            entity_type="rule",
            entity_id=new_rule.id,
            details=f"Force created {severity.value} rule after similarity review"
        )
        db.add(audit)
        db.commit()
        
        return {
            "status": "success",
            "message": "Rule created successfully",
            "rule": {
                "id": new_rule.id,
                "rule_text": new_rule.rule_text,
                "severity": new_rule.severity.value,
                "version": new_rule.version,
                "is_active": new_rule.is_active
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/rules/{rule_id}")
async def update_rule(
    rule_id: int,
    rule_data: RuleUpdate,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Super Admin endpoint: Update rule text (creates new version).
    
    HUMAN-ONLY: Rule text must be manually edited by Super Admin.
    """
    try:
        # Validate human input
        if not rule_data.rule_text or not rule_data.rule_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Rule text is required and must be manually entered"
            )
        
        old_rule = db.query(Rule).filter(Rule.id == rule_id).first()
        
        if not old_rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        # Deactivate old version
        old_rule.is_active = False
        
        # Create new version (human-edited)
        new_rule = Rule(
            rule_text=rule_data.rule_text,
            severity=old_rule.severity,
            is_active=True,
            version=old_rule.version + 1,
            parent_rule_id=rule_id,
            created_by=user_id
        )
        
        db.add(new_rule)
        db.commit()
        db.refresh(new_rule)
        
        # Update embedding (derived data)
        embedding_service = get_embedding_service()
        try:
            embedding_service.delete_rule_embedding(rule_id)
            embedding_service.store_rule_embedding(new_rule.id, new_rule.rule_text)
        except Exception as e:
            import logging
            logging.warning(f"Failed to update embedding: {e}")
        
        # Audit log
        audit = AuditLog(
            user_id=user_id,
            action="update_rule",
            entity_type="rule",
            entity_id=new_rule.id,
            details=f"Updated rule {rule_id} to version {new_rule.version} - Human-edited"
        )
        db.add(audit)
        db.commit()
        
        return {
            "status": "success",
            "message": "Rule updated successfully",
            "old_rule_id": rule_id,
            "new_rule": {
                "id": new_rule.id,
                "rule_text": new_rule.rule_text,
                "version": new_rule.version,
                "source": "human_edited"
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/rules/{rule_id}")
async def deactivate_rule(
    rule_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Super Admin endpoint: Soft delete (deactivate) rule.
    Human decision only.
    """
    try:
        rule = db.query(Rule).filter(Rule.id == rule_id).first()
        
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        # Soft delete
        rule.is_active = False
        db.commit()
        
        # Delete embedding (derived data)
        embedding_service = get_embedding_service()
        try:
            embedding_service.delete_rule_embedding(rule_id)
        except Exception as e:
            import logging
            logging.warning(f"Failed to delete embedding: {e}")
        
        # Audit log
        audit = AuditLog(
            user_id=user_id,
            action="deactivate_rule",
            entity_type="rule",
            entity_id=rule_id,
            details="Deactivated rule - Human decision"
        )
        db.add(audit)
        db.commit()
        
        return {
            "status": "success",
            "message": f"Rule {rule_id} deactivated successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules")
async def get_all_rules(
    include_inactive: bool = False,
    db: Session = Depends(get_db)
):
    """
    Super Admin endpoint: Get all rules with versioning.
    Shows human-created rules only.
    """
    query = db.query(Rule)
    
    if not include_inactive:
        query = query.filter(Rule.is_active == True)
    
    rules = query.order_by(Rule.created_at.desc()).all()
    
    result = []
    for r in rules:
        result.append({
            "id": r.id,
            "rule_text": r.rule_text,
            "severity": r.severity.value,
            "is_active": r.is_active,
            "version": r.version,
            "parent_rule_id": r.parent_rule_id,
            "created_by": r.created_by,
            "created_at": r.created_at.isoformat(),
            "source": "human_created"
        })
    
    return {"rules": result, "total": len(result)}


@router.post("/documents/upload")
async def upload_reference_document(
    file: UploadFile = File(...),
    user_id: int = 0,
    db: Session = Depends(get_db)
):
    """
    Upload document as REFERENCE ONLY.
    
    CRITICAL: Document is NOT parsed for rule extraction.
    Super Admin reads document and manually writes rules.
    """
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.md']
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save document as reference only
        upload_dir = Path("reference_documents")
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Audit log (document upload, NOT rule creation)
        audit = AuditLog(
            user_id=user_id,
            action="upload_reference_document",
            entity_type="document",
            entity_id=0,
            details=f"Uploaded reference document: {file.filename} - FOR HUMAN REVIEW ONLY"
        )
        db.add(audit)
        db.commit()
        
        return {
            "status": "success",
            "message": "Document uploaded as reference material",
            "filename": file.filename,
            "path": str(file_path),
            "note": "This document is for human review only. No rules will be auto-generated."
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
async def list_reference_documents():
    """
    List uploaded reference documents.
    These are for human review only.
    """
    try:
        upload_dir = Path("reference_documents")
        if not upload_dir.exists():
            return {"documents": [], "total": 0}
        
        documents = []
        for file_path in upload_dir.iterdir():
            if file_path.is_file():
                documents.append({
                    "filename": file_path.name,
                    "size_bytes": file_path.stat().st_size,
                    "uploaded_at": file_path.stat().st_mtime,
                    "purpose": "Human reference only"
                })
        
        return {
            "documents": documents,
            "total": len(documents),
            "note": "These documents are reference material only. Rules must be manually created."
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
