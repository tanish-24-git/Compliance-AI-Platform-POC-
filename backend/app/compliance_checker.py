"""
Compliance checker - final decision orchestrator.
Combines rule engine + AI reviewer for deterministic compliance decisions.
Rules ALWAYS override AI output.
"""

import logging
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session

from app.models import Rule, Violation, Submission, SubmissionStatus
from app.rule_engine import RuleEngine
from app.reviewer import review_compliance

logger = logging.getLogger(__name__)


class ComplianceChecker:
    """Final compliance decision maker - orchestrates rule engine and AI reviewer"""

    def __init__(self, db: Session):
        """
        Initialize compliance checker.
        
        Args:
            db: Database session
        """
        self.db = db
        self.rule_engine = RuleEngine(db)

    def check_compliance(self, submission_id: int, generated_content: str) -> Dict:
        """
        Perform complete compliance check on generated content.
        
        Flow:
        1. Rule engine checks (authoritative)
        2. AI reviewer checks (advisory)
        3. Backend makes final decision (rules override AI)
        
        Args:
            submission_id: Database ID of submission
            generated_content: Content to check
        
        Returns:
            Compliance result with decision, violations, and reasoning
        """
        logger.info(f"Starting compliance check for submission {submission_id}")
        
        # Step 1: Rule engine check (authoritative)
        rule_violations = self.rule_engine.check_violations(generated_content)
        
        # Step 2: Get active rules for AI reviewer
        active_rules = self.rule_engine.get_active_rules()
        rules_for_ai = [
            {"rule_text": r.rule_text, "severity": r.severity.value, "id": r.id}
            for r in active_rules
        ]
        
        # Step 3: AI reviewer check (advisory)
        ai_review = {}
        try:
            ai_review = review_compliance(generated_content, rules_for_ai)
        except Exception as e:
            logger.warning(f"AI review failed, proceeding with rule engine only: {e}")
            ai_review = {"violations": [], "recommendations": "AI review unavailable"}
        
        # Step 4: Make final decision (rules ALWAYS override)
        is_approved, decision_reason = self.rule_engine.enforce_hard_rules(
            generated_content, 
            rule_violations
        )
        
        # Step 5: Handle soft rule annotations
        soft_annotations = self.rule_engine.annotate_soft_rules(rule_violations)
        
        # Step 6: Store violations in database
        self._store_violations(submission_id, rule_violations)
        
        # Step 7: Update submission status
        self._update_submission_status(
            submission_id, 
            is_approved,
            generated_content
        )
        
        # Step 8: Build result
        result = {
            "submission_id": submission_id,
            "is_approved": is_approved,
            "compliance_status": "approved" if is_approved else "rejected",
            "decision_reason": decision_reason,
            "rule_violations": rule_violations,
            "ai_review": ai_review,
            "soft_annotations": soft_annotations,
            "total_violations": len(rule_violations),
            "hard_violations": len([v for v in rule_violations if v["severity"] == "hard"]),
            "soft_violations": len([v for v in rule_violations if v["severity"] == "soft"])
        }
        
        logger.info(
            f"Compliance check complete: {result['compliance_status']} "
            f"({result['total_violations']} violations)"
        )
        
        return result

    def _store_violations(self, submission_id: int, violations: List[Dict]):
        """Store detected violations in database"""
        try:
            for v in violations:
                violation = Violation(
                    submission_id=submission_id,
                    rule_id=v["rule_id"],
                    violated_text=v["violated_text"],
                    severity=v["severity"],
                    context=v["context"]
                )
                self.db.add(violation)
            
            self.db.commit()
            logger.info(f"Stored {len(violations)} violations for submission {submission_id}")
        
        except Exception as e:
            logger.error(f"Failed to store violations: {e}")
            self.db.rollback()

    def _update_submission_status(self, submission_id: int, is_approved: bool, 
                                  generated_content: str):
        """Update submission with compliance result"""
        try:
            submission = self.db.query(Submission).filter(
                Submission.id == submission_id
            ).first()
            
            if submission:
                submission.status = SubmissionStatus.APPROVED if is_approved else SubmissionStatus.REJECTED
                submission.compliance_status = "approved" if is_approved else "rejected"
                submission.generated_content = generated_content
                
                from datetime import datetime
                submission.completed_at = datetime.utcnow()
                
                self.db.commit()
                logger.info(f"Updated submission {submission_id} status to {submission.status.value}")
        
        except Exception as e:
            logger.error(f"Failed to update submission status: {e}")
            self.db.rollback()


def check_content_compliance(db: Session, submission_id: int, 
                            generated_content: str) -> Dict:
    """
    Convenience function to check content compliance.
    
    Args:
        db: Database session
        submission_id: Submission ID
        generated_content: Generated content to check
    
    Returns:
        Compliance result dictionary
    """
    checker = ComplianceChecker(db)
    return checker.check_compliance(submission_id, generated_content)
