"""Admin routes for monitoring and analytics"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.models import Violation, Submission, Rule

router = APIRouter()


@router.get("/violations")
async def get_violations(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Admin endpoint: Get all violations with filtering.
    Returns violations with submission and rule details.
    """
    violations = db.query(Violation).order_by(
        Violation.detected_at.desc()
    ).limit(limit).offset(offset).all()
    
    result = []
    for v in violations:
        submission = db.query(Submission).filter(Submission.id == v.submission_id).first()
        rule = db.query(Rule).filter(Rule.id == v.rule_id).first()
        
        result.append({
            "id": v.id,
            "submission_id": v.submission_id,
            "user_id": submission.user_id if submission else None,
            "rule_id": v.rule_id,
            "rule_text": rule.rule_text if rule else "Rule deleted",
            "severity": v.severity.value,
            "violated_text": v.violated_text,
            "context": v.context,
            "detected_at": v.detected_at.isoformat()
        })
    
    return {"violations": result, "total": len(result)}


@router.get("/analytics/rules")
async def get_rule_analytics(db: Session = Depends(get_db)):
    """
    Admin endpoint: Get rule hit frequency analytics.
    Returns which rules are violated most often.
    """
    # Count violations per rule
    rule_stats = db.query(
        Rule.id,
        Rule.rule_text,
        Rule.severity,
        func.count(Violation.id).label("violation_count")
    ).outerjoin(Violation).group_by(Rule.id).all()
    
    analytics = []
    for rule_id, rule_text, severity, count in rule_stats:
        analytics.append({
            "rule_id": rule_id,
            "rule_text": rule_text,
            "severity": severity.value,
            "violation_count": count
        })
    
    # Sort by violation count
    analytics.sort(key=lambda x: x["violation_count"], reverse=True)
    
    return {"rule_analytics": analytics}


@router.get("/submissions")
async def get_all_submissions(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Admin endpoint: Get all past generations.
    """
    submissions = db.query(Submission).order_by(
        Submission.created_at.desc()
    ).limit(limit).offset(offset).all()
    
    result = []
    for s in submissions:
        violation_count = db.query(Violation).filter(
            Violation.submission_id == s.id
        ).count()
        
        result.append({
            "id": s.id,
            "user_id": s.user_id,
            "prompt": s.prompt[:100] + "..." if len(s.prompt) > 100 else s.prompt,
            "status": s.status.value,
            "compliance_status": s.compliance_status,
            "violation_count": violation_count,
            "created_at": s.created_at.isoformat()
        })
    
    return {"submissions": result, "total": len(result)}
