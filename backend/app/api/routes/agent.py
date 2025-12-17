"""Agent routes for content generation"""

from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pathlib import Path
import shutil
import logging

from app.core.database import get_db
from app.models.models import Submission, SubmissionStatus, ContentChunk, AuditLog, User
from app.services.document_service import parse_document
from app.services.chunking_service import chunk_content
from app.services.prompt_service import enhance_user_prompt
from app.services.generation_service import generate_content
from app.services.compliance_service import check_content_compliance

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate")
async def generate_compliant_content(
    user_id: int = Form(...),
    prompt: str = Form(...),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Agent endpoint: Generate compliant content with web search enhancement.
    
    Flow:
    1. Create submission
    2. Web search for relevant information
    3. Parse uploaded file (if any)
    4. Enhance prompt with rules + web research
    5. Generate content with Gemini
    6. Review with Groq + Rule Engine
    7. Make final compliance decision
    8. Return result with web research
    """
    from app.services.web_search_service import get_search_service
    
    try:
        # Create submission record
        submission = Submission(
            user_id=user_id,
            prompt=prompt,
            status=SubmissionStatus.PROCESSING
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        # WEB SEARCH: Research the topic
        web_research = []
        research_sources = []
        search_service = get_search_service()
        
        if search_service.enabled:
            keywords = search_service.extract_keywords(prompt)
            search_results = await search_service.research(keywords, max_results=3)
            
            for result in search_results:
                web_research.append(f"{result['title']}: {result['snippet']}")
                research_sources.append(result['url'])
            
            logger.info(f"Web research: {len(web_research)} results for '{keywords}'")
        
        # Parse uploaded file if provided
        file_content = None
        file_type = None
        
        if file:
            # Save uploaded file temporarily
            upload_dir = Path("uploads")
            upload_dir.mkdir(exist_ok=True)
            
            file_path = upload_dir / f"{submission.id}_{file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Parse file
            file_type = file.filename.split(".")[-1].lower()
            try:
                file_content = parse_document(str(file_path), file_type)
                submission.uploaded_file_path = str(file_path)
                submission.uploaded_file_type = file_type
                db.commit()
                
                # Chunk file content
                file_chunks = chunk_content(file_content, "uploaded_file")
                for chunk_data in file_chunks:
                    chunk = ContentChunk(
                        submission_id=submission.id,
                        **chunk_data
                    )
                    db.add(chunk)
                db.commit()
                
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to parse uploaded file: {str(e)}"
                )
        
        # Enhance prompt with compliance rules + web research
        enhanced_prompt = enhance_user_prompt(
            db, prompt, file_content, file_type
        )
        
        # Add web research to prompt if available
        if web_research:
            research_context = "\n\nWEB RESEARCH FINDINGS:\n" + "\n".join(
                f"- {research}" for research in web_research
            )
            enhanced_prompt += research_context
        
        # Chunk prompt
        prompt_chunks = chunk_content(prompt, "prompt")
        for chunk_data in prompt_chunks:
            chunk = ContentChunk(
                submission_id=submission.id,
                **chunk_data
            )
            db.add(chunk)
        db.commit()
        
        # Generate content with Gemini
        try:
            generated_content = generate_content(enhanced_prompt)
        except Exception as e:
            submission.status = SubmissionStatus.FAILED
            db.commit()
            raise HTTPException(
                status_code=500,
                detail=f"Content generation failed: {str(e)}"
            )
        
        # Chunk generated content
        gen_chunks = chunk_content(generated_content, "generated")
        for chunk_data in gen_chunks:
            chunk = ContentChunk(
                submission_id=submission.id,
                **chunk_data
            )
            db.add(chunk)
        db.commit()
        
        # Check compliance
        compliance_result = check_content_compliance(
            db, submission.id, generated_content
        )
        
        # Log audit trail only if valid user
        if user_id > 0:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                audit = AuditLog(
                    user_id=user_id,
                    action="generate_content",
                    entity_type="submission",
                    entity_id=submission.id,
                    details=f"Status: {compliance_result['compliance_status']}, Violations: {compliance_result['total_violations']}"
                )
                db.add(audit)
                db.commit()
        
        return {
            "submission_id": submission.id,
            "generated_content": generated_content,
            "web_research": web_research,
            "research_sources": research_sources,
            "compliance_status": compliance_result["compliance_status"],
            "is_approved": compliance_result["is_approved"],
            "violations": compliance_result["rule_violations"],
            "total_violations": compliance_result["total_violations"],
            "hard_violations": compliance_result["hard_violations"],
            "soft_violations": compliance_result["soft_violations"],
            "decision_reason": compliance_result["decision_reason"],
            "soft_annotations": compliance_result["soft_annotations"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/submissions/{submission_id}")
async def get_submission(submission_id: int, db: Session = Depends(get_db)):
    """Get submission details by ID"""
    from app.models.models import Violation
    
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    violations = db.query(Violation).filter(Violation.submission_id == submission_id).all()
    
    return {
        "id": submission.id,
        "user_id": submission.user_id,
        "prompt": submission.prompt,
        "generated_content": submission.generated_content,
        "status": submission.status.value,
        "compliance_status": submission.compliance_status,
        "created_at": submission.created_at.isoformat(),
        "violations": [
            {
                "rule_id": v.rule_id,
                "violated_text": v.violated_text,
                "severity": v.severity.value,
                "context": v.context
            }
            for v in violations
        ]
    }
