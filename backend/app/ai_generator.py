"""
Gemini AI content generator.
Uses Google's Gemini API for compliant content generation.
"""

import os
import logging
from typing import Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeminiGenerator:
    """Content generation using Gemini API"""

    def __init__(self):
        """Initialize Gemini API client"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        # Use gemini-1.5-flash for faster response and better availability
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("Gemini generator initialized (model: gemini-1.5-flash)")

    def generate_content(self, enhanced_prompt: str) -> str:
        """
        Generate content using Gemini API.
        
        Args:
            enhanced_prompt: Compliance-enhanced prompt
        
        Returns:
            Generated content
        
        Raises:
            Exception: If generation fails
        """
        try:
            logger.info("Generating content with Gemini...")
            
            response = self.model.generate_content(enhanced_prompt)
            
            if not response or not response.text:
                raise ValueError("Gemini returned empty response")
            
            generated_text = response.text.strip()
            logger.info(f"Generated {len(generated_text)} characters of content")
            
            return generated_text
        
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise Exception(f"Content generation failed: {str(e)}")

    def generate_with_retry(self, enhanced_prompt: str, max_retries: int = 2) -> str:
        """
        Generate content with retry logic.
        
        Args:
            enhanced_prompt: Enhanced prompt
            max_retries: Maximum retry attempts
        
        Returns:
            Generated content
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                return self.generate_content(enhanced_prompt)
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    logger.warning(f"Generation attempt {attempt + 1} failed, retrying...")
                    continue
                else:
                    logger.error(f"All {max_retries + 1} generation attempts failed")
                    raise last_error


# Singleton instance
_gemini_generator: Optional[GeminiGenerator] = None


def get_gemini_generator() -> GeminiGenerator:
    """Get or create Gemini generator singleton"""
    global _gemini_generator
    if _gemini_generator is None:
        _gemini_generator = GeminiGenerator()
    return _gemini_generator


def generate_content(enhanced_prompt: str) -> str:
    """
    Convenience function to generate content.
    
    Args:
        enhanced_prompt: Compliance-enhanced prompt
    
    Returns:
        Generated content
    """
    generator = get_gemini_generator()
    return generator.generate_with_retry(enhanced_prompt)
