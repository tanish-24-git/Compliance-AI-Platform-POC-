"""
Prompt enhancement service.
Injects compliance rules into prompts.
"""

from app.prompt_enhancer import enhance_user_prompt as _enhance_user_prompt

# Re-export for service layer
enhance_user_prompt = _enhance_user_prompt
