"""
SQLAlchemy ORM models.
Moved from app/models.py to app/models/models.py for better organization.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class UserRole(enum.Enum):
    """User roles for governance"""
    AGENT = "agent"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class RuleSeverity(enum.Enum):
    """Rule severity levels - HARD rules block, SOFT rules annotate"""
    HARD = "hard"
    SOFT = "soft"


class SubmissionStatus(enum.Enum):
    """Status of content generation submissions"""
    PENDING = "pending"
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"
    FAILED = "failed"


class User(Base):
    """User model with role-based access"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    submissions = relationship("Submission", back_populates="user")
    rules_created = relationship("Rule", back_populates="creator")
    audit_logs = relationship("AuditLog", back_populates="user")


class Rule(Base):
    """Compliance rules - the authoritative source for compliance enforcement"""
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_text = Column(Text, nullable=False)
    severity = Column(SQLEnum(RuleSeverity), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    version = Column(Integer, default=1, nullable=False)
    parent_rule_id = Column(Integer, ForeignKey("rules.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="rules_created")
    parent_rule = relationship("Rule", remote_side=[id])
    violations = relationship("Violation", back_populates="rule")


class Submission(Base):
    """User content generation requests"""
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    uploaded_file_path = Column(String(500), nullable=True)
    uploaded_file_type = Column(String(50), nullable=True)
    generated_content = Column(Text, nullable=True)
    status = Column(SQLEnum(SubmissionStatus), default=SubmissionStatus.PENDING, nullable=False, index=True)
    compliance_status = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="submissions")
    chunks = relationship("ContentChunk", back_populates="submission")
    violations = relationship("Violation", back_populates="submission")


class ContentChunk(Base):
    """Tokenized content chunks with metadata"""
    __tablename__ = "content_chunks"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_position = Column(Integer, nullable=False)
    token_count = Column(Integer, nullable=False)
    source_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    submission = relationship("Submission", back_populates="chunks")


class Violation(Base):
    """Rule violations detected during compliance checking"""
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    rule_id = Column(Integer, ForeignKey("rules.id"), nullable=False)
    violated_text = Column(Text, nullable=False)
    severity = Column(SQLEnum(RuleSeverity), nullable=False)
    context = Column(Text, nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    submission = relationship("Submission", back_populates="violations")
    rule = relationship("Rule", back_populates="violations")


class AuditLog(Base):
    """Complete audit trail for governance and compliance"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")
