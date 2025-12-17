"""
Groq compliance reviewer.
Strict compliance review using Groq API - AI never makes final approval.
"""

import os
import logging
from typing import Dict, List, Optional
import json
from groq import Groq

logger = logging.getLogger(__name__)


class GroqReviewer:
    """Compliance review using Groq API"""

    def __init__(self):
        """Initialize Groq API client"""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-70b-versatile"  # Fast and capable model
        logger.info("Groq reviewer initialized")

    def review_content(self, content: str, rules: List[Dict]) -> Dict:
        """
        Review generated content against compliance rules.
        
        Args:
            content: Generated content to review
            rules: List of active rules with text and severity
        
        Returns:
            Review result with violations and recommendations
        """
        try:
            # Build review prompt
            review_prompt = self._build_review_prompt(content, rules)
            
            logger.info("Reviewing content with Groq...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a strict compliance reviewer for regulated financial/insurance content. Your job is to identify rule violations, not to approve content. Be thorough and precise."
                    },
                    {
                        "role": "user",
                        "content": review_prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistency
                max_tokens=2000
            )
            
            review_text = response.choices[0].message.content
            
            # Parse review into structured format
            review_result = self._parse_review(review_text)
            
            logger.info(f"Review complete: {len(review_result.get('violations', []))} violations found")
            
            return review_result
        
        except Exception as e:
            logger.error(f"Groq review failed: {e}")
            raise Exception(f"Compliance review failed: {str(e)}")

    def _build_review_prompt(self, content: str, rules: List[Dict]) -> str:
        """Build structured review prompt"""
        
        rules_text = "\n".join([
            f"{i+1}. [{r['severity'].upper()}] {r['rule_text']}"
            for i, r in enumerate(rules)
        ])
        
        prompt = f"""Review the following generated content against compliance rules.

COMPLIANCE RULES:
{rules_text}

GENERATED CONTENT:
{content}

INSTRUCTIONS:
1. Check the content against EACH rule
2. Identify ANY violations (even minor ones)
3. For each violation, specify:
   - Which rule was violated
   - The specific text that violates the rule
   - Why it's a violation
4. Provide your analysis in this exact format:

VIOLATIONS:
[If violations found, list each as: "Rule X: [reason] - Violated text: [quote]"]
[If no violations, write: "NONE"]

RECOMMENDATIONS:
[Suggest improvements even if no violations found]

Be strict and thorough. When in doubt, flag it as a violation.
"""
        return prompt

    def _parse_review(self, review_text: str) -> Dict:
        """
        Parse Groq's review text into structured format.
        
        Returns:
            Dictionary with violations list and recommendations
        """
        result = {
            "violations": [],
            "recommendations": "",
            "raw_review": review_text
        }
        
        # Simple parsing - look for VIOLATIONS and RECOMMENDATIONS sections
        sections = review_text.split("RECOMMENDATIONS:")
        
        if len(sections) >= 2:
            violations_section = sections[0]
            recommendations_section = sections[1].strip()
            result["recommendations"] = recommendations_section
            
            # Parse violations
            if "VIOLATIONS:" in violations_section:
                violations_text = violations_section.split("VIOLATIONS:")[1].strip()
                
                if violations_text.upper() != "NONE" and violations_text.strip():
                    # Split by lines and parse each violation
                    lines = [l.strip() for l in violations_text.split("\n") if l.strip()]
                    for line in lines:
                        if line and not line.startswith("RECOMMENDATIONS"):
                            result["violations"].append({
                                "description": line,
                                "source": "groq_review"
                            })
        
        return result


# Singleton instance
_groq_reviewer: Optional[GroqReviewer] = None


def get_groq_reviewer() -> GroqReviewer:
    """Get or create Groq reviewer singleton"""
    global _groq_reviewer
    if _groq_reviewer is None:
        _groq_reviewer = GroqReviewer()
    return _groq_reviewer


def review_compliance(content: str, rules: List[Dict]) -> Dict:
    """
    Convenience function to review content compliance.
    
    Args:
        content: Generated content
        rules: Active compliance rules
    
    Returns:
        Review result dictionary
    """
    reviewer = get_groq_reviewer()
    return reviewer.review_content(content, rules)
