"""
Database initialization and seeding.
Auto-creates users and sample rules on startup.
"""

import logging
from sqlalchemy.orm import Session
from app.models.models import User, Rule, UserRole, RuleSeverity
from app.services.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)


def seed_users(db: Session) -> bool:
    """
    Seed default users if they don't exist.
    Returns True if seeding was performed.
    """
    try:
        # Check if users already exist
        existing_count = db.query(User).count()
        if existing_count > 0:
            logger.info(f"Users already exist ({existing_count}). Skipping user seed.")
            return False
        
        # Create default users
        users = [
            User(
                id=1,
                username="agent_user",
                email="agent@compliance.ai",
                role=UserRole.AGENT
            ),
            User(
                id=2,
                username="admin_user",
                email="admin@compliance.ai",
                role=UserRole.ADMIN
            ),
            User(
                id=3,
                username="superadmin_user",
                email="superadmin@compliance.ai",
                role=UserRole.SUPER_ADMIN
            )
        ]
        
        for user in users:
            db.add(user)
        
        db.commit()
        logger.info(f"✅ Seeded {len(users)} users")
        return True
        
    except Exception as e:
        logger.error(f"Failed to seed users: {e}")
        db.rollback()
        return False


def seed_rules(db: Session) -> bool:
    """
    Seed sample compliance rules if they don't exist.
    Returns True if seeding was performed.
    """
    try:
        # Check if rules already exist
        existing_count = db.query(Rule).count()
        if existing_count > 0:
            logger.info(f"Rules already exist ({existing_count}). Skipping rule seed.")
            return False
        
        # Sample compliance rules
        rules_data = [
            {
                "rule_text": 'Content must not include prohibited terms such as "guaranteed returns", "risk-free", or "no risk"',
                "severity": RuleSeverity.HARD,
            },
            {
                "rule_text": 'All financial content must include the disclaimer: "Past performance does not guarantee future results. Investments carry risk."',
                "severity": RuleSeverity.HARD,
            },
            {
                "rule_text": "Content must maintain a professional, neutral tone without emotional language or urgency tactics",
                "severity": RuleSeverity.SOFT,
            },
            {
                "rule_text": "Personal data and PII must never be included in generated content examples",
                "severity": RuleSeverity.HARD,
            },
            {
                "rule_text": "Content should use clear, accessible language avoiding excessive jargon when possible",
                "severity": RuleSeverity.SOFT,
            }
        ]
        
        embedding_service = get_embedding_service()
        created_rules = []
        
        for rule_data in rules_data:
            rule = Rule(
                rule_text=rule_data["rule_text"],
                severity=rule_data["severity"],
                is_active=True,
                version=1,
                created_by=3  # Super Admin
            )
            db.add(rule)
            db.commit()
            db.refresh(rule)
            
            # Store embedding
            try:
                embedding_service.store_rule_embedding(rule.id, rule.rule_text)
            except Exception as e:
                logger.warning(f"Failed to store embedding for rule {rule.id}: {e}")
            
            created_rules.append(rule)
        
        logger.info(f"✅ Seeded {len(created_rules)} compliance rules")
        return True
        
    except Exception as e:
        logger.error(f"Failed to seed rules: {e}")
        db.rollback()
        return False


def auto_seed_database(db: Session):
    """
    Automatically seed database with users and rules on startup.
    Safe to call multiple times - only seeds if empty.
    """
    logger.info("🌱 Auto-seeding database...")
    
    users_seeded = seed_users(db)
    rules_seeded = seed_rules(db)
    
    if users_seeded or rules_seeded:
        logger.info("✅ Database seeding complete")
    else:
        logger.info("ℹ️  Database already seeded")
