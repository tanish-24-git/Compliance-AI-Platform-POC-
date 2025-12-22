from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID
from app.models.content import ComplianceStatus, InputType


class ContentGenerateRequest(BaseModel):
    """Schema for content generation request"""
    prompt: str = Field(..., min_length=5)
    use_prompt_enhancer: bool = False
    user_id: UUID = Field(default=UUID('00000000-0000-0000-0000-000000000001'))


class RuleTriggered(BaseModel):
    """Schema for triggered rule info"""
    rule_id: UUID
    rule_text: str
    category: str
    severity: str
    status: str  # "triggered" or "violated"


class ContentGenerateResponse(BaseModel):
    """Schema for content generation response"""
    submission_id: UUID
    final_content: str
    compliance_status: ComplianceStatus
    rules_triggered: List[RuleTriggered]
    created_at: datetime


class DocumentCheckRequest(BaseModel):
    """Schema for document compliance check request"""
    user_id: UUID
    filename: str


class ViolationDetail(BaseModel):
    """Schema for violation details"""
    chunk_text: str
    violated_rules: List[RuleTriggered]
    page_number: Optional[int] = None
    section: Optional[str] = None


class DocumentCheckResponse(BaseModel):
    """Schema for document check response"""
    submission_id: UUID
    compliance_status: ComplianceStatus
    violations: List[ViolationDetail]
    rules_triggered: List[RuleTriggered]


class ContentRewriteRequest(BaseModel):
    """Schema for content rewrite request"""
    submission_id: UUID
    violation_text: str


class ContentApprovalRequest(BaseModel):
    """Schema for admin approval"""
    admin_id: UUID
    status: str  # "approved" or "rejected"
    notes: Optional[str] = None


class ContentListResponse(BaseModel):
    """Schema for content list item"""
    submission_id: UUID
    input_type: InputType
    compliance_status: ComplianceStatus
    created_at: datetime
    approval_status: Optional[str]
    
    class Config:
        from_attributes = True
