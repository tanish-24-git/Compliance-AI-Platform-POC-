"""
Database seeding script.
Updated imports for new structure.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.core.database import get_db_session, init_db
from app.models.models import User, Rule, UserRole, RuleSeverity
from app.services.embedding_service import get_embedding_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_users(db: Session):
    """Create sample users for each role"""
    users = [
        User(
            username="agent_user",
            email="agent@compliance.com",
            role=UserRole.AGENT
        ),
        User(
            username="admin_user",
            email="admin@compliance.com",
            role=UserRole.ADMIN
        ),
        User(
            username="superadmin_user",
            email="superadmin@compliance.com",
            role=UserRole.SUPER_ADMIN
        )
    ]
    
    for user in users:
        db.add(user)
    
    db.commit()
    logger.info(f"Created {len(users)} users")
    return users


def seed_rules(db: Session, super_admin_id: int):
    """Create sample compliance rules"""
    rules = [
        {
            "rule_text": 'Content must not include prohibited terms such as "guaranteed returns", "risk-free", or "no risk"',
            "severity": RuleSeverity.HARD,
            "created_by": super_admin_id
        },
        {
            "rule_text": 'All financial content must include the disclaimer: "Past performance does not guarantee future results. Investments carry risk."',
            "severity": RuleSeverity.HARD,
            "created_by": super_admin_id
        },
        {
            "rule_text": "Content must maintain a professional, neutral tone without emotional language or urgency tactics",
            "severity": RuleSeverity.SOFT,
            "created_by": super_admin_id
        },
        {
            "rule_text": "Personal data and PII must never be included in generated content examples",
            "severity": RuleSeverity.HARD,
            "created_by": super_admin_id
        },
        {
            "rule_text": "Content should use clear, accessible language avoiding excessive jargon when possible",
            "severity": RuleSeverity.SOFT,
            "created_by": super_admin_id
        }
    ]
    
    created_rules = []
    embedding_service = get_embedding_service()
    
    for rule_data in rules:
        rule = Rule(
            rule_text=rule_data["rule_text"],
            severity=rule_data["severity"],
            is_active=True,
            version=1,
            created_by=rule_data["created_by"]
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        
        # Store embedding in Pinecone
        try:
            embedding_service.store_rule_embedding(rule.id, rule.rule_text)
            logger.info(f"Created rule {rule.id} with embedding")
        except Exception as e:
            logger.warning(f"Failed to store embedding for rule {rule.id}: {e}")
        
        created_rules.append(rule)
    
    logger.info(f"Created {len(created_rules)} compliance rules")
    return created_rules


def main():
    """Main seeding function"""
    try:
        logger.info("Starting database seeding...")
        
        # Initialize database
        init_db()
        
        # Get database session
        db = get_db_session()
        
        try:
            # Check if already seeded
            existing_users = db.query(User).count()
            if existing_users > 0:
                logger.warning("Database already contains users. Re-seeding will add duplicate data.")
                # In Docker, automatically proceed without prompting
                logger.info("Proceeding with re-seed...")
            
            # Seed users
            users = seed_users(db)
            
            # Find super admin
            super_admin = next(u for u in users if u.role == UserRole.SUPER_ADMIN)
            
            # Seed rules
            rules = seed_rules(db, super_admin.id)
            
            logger.info("=" * 60)
            logger.info("DATABASE SEEDING COMPLETE")
            logger.info("=" * 60)
            logger.info(f"Created {len(users)} users:")
            for user in users:
                logger.info(f"  - {user.username} ({user.role.value}) - ID: {user.id}")
            logger.info(f"\nCreated {len(rules)} compliance rules:")
            for rule in rules:
                logger.info(f"  - [{rule.severity.value.upper()}] {rule.rule_text[:60]}...")
            logger.info("=" * 60)
            
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        raise


if __name__ == "__main__":
    main()
