"""
Content generation service.
Gemini API integration.
"""

from app.ai_generator import generate_content as _generate_content

# Re-export for service layer
generate_content = _generate_content
