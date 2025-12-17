"""
Compliance checking service.
Final compliance decision orchestration.
"""

from app.compliance_checker import check_content_compliance as _check_content_compliance

# Re-export for service layer
check_content_compliance = _check_content_compliance
