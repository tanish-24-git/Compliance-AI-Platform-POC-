"""
Prompt enhancer - converts weak prompts into compliance-aware prompts.
Injects active rules to reduce retries and token waste.
"""

import logging
from sqlalchemy.orm import Session

from app.rule_engine import RuleEngine

logger = logging.getLogger(__name__)


class PromptEnhancer:
    """Enhance user prompts with compliance context"""

    def __init__(self, db: Session):
        """
        Initialize with database session for rule access.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.rule_engine = RuleEngine(db)

    def enhance_prompt(self, user_prompt: str, context: str = "") -> str:
        """
        Convert weak user prompt into compliance-aware prompt.
        
        Args:
            user_prompt: Original user prompt
            context: Optional additional context (e.g., from uploaded files)
        
        Returns:
            Enhanced prompt with compliance rules injected
        """
        # Get active rules formatted for injection
        rules_section = self.rule_engine.get_rules_for_prompt_injection()
        
        # Build enhanced prompt
        enhanced = f"""You are a compliance-first content generator for regulated financial/insurance environments.

{rules_section}

INSTRUCTIONS:
1. Generate content that strictly adheres to ALL compliance rules above
2. HARD rules are non-negotiable - any violation will result in content rejection
3. SOFT rules should be followed when possible - violations will be flagged
4. Maintain professional, clear, and legally sound language
5. If context is provided, incorporate it while ensuring compliance

USER REQUEST:
{user_prompt}
"""

        if context:
            enhanced += f"\n\nADDITIONAL CONTEXT:\n{context}\n"

        enhanced += """
IMPORTANT: Your response must be compliant with all HARD rules. Generate content now:
"""

        logger.info("Enhanced user prompt with compliance rules")
        return enhanced

    def enhance_with_file_context(self, user_prompt: str, file_content: str, 
                                  file_type: str) -> str:
        """
        Enhance prompt with uploaded file context.
        
        Args:
            user_prompt: User's prompt
            file_content: Parsed file content
            file_type: Type of file (pdf, docx, md)
        
        Returns:
            Enhanced prompt with file context
        """
        context = f"[Content from uploaded {file_type.upper()} file]:\n{file_content}"
        return self.enhance_prompt(user_prompt, context)


def enhance_user_prompt(db: Session, user_prompt: str, 
                       file_content: str = None, file_type: str = None) -> str:
    """
    Convenience function to enhance a user prompt.
    
    Args:
        db: Database session
        user_prompt: User's original prompt
        file_content: Optional file content
        file_type: Optional file type
    
    Returns:
        Enhanced compliance-aware prompt
    """
    enhancer = PromptEnhancer(db)
    
    if file_content:
        return enhancer.enhance_with_file_context(user_prompt, file_content, file_type)
    else:
        return enhancer.enhance_prompt(user_prompt)
