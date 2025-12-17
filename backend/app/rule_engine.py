"""
Rule engine - the authoritative source for compliance enforcement.
Rules from PostgreSQL ALWAYS override AI output.
"""

import logging
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session

from app.models import Rule, RuleSeverity

logger = logging.getLogger(__name__)


class RuleEngine:
    """Enforce compliance rules with HARD/SOFT severity handling"""

    def __init__(self, db: Session):
        """
        Initialize rule engine with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_active_rules(self) -> List[Rule]:
        """
        Fetch all active rules from PostgreSQL.
        These are the authoritative rules for compliance.
        """
        try:
            rules = self.db.query(Rule).filter(Rule.is_active == True).all()
            logger.info(f"Loaded {len(rules)} active rules")
            return rules
        except Exception as e:
            logger.error(f"Failed to fetch active rules: {e}")
            return []

    def categorize_rules(self) -> Tuple[List[Rule], List[Rule]]:
        """
        Categorize rules by severity.
        
        Returns:
            Tuple of (hard_rules, soft_rules)
        """
        rules = self.get_active_rules()
        hard_rules = [r for r in rules if r.severity == RuleSeverity.HARD]
        soft_rules = [r for r in rules if r.severity == RuleSeverity.SOFT]
        
        logger.info(f"Categorized rules: {len(hard_rules)} HARD, {len(soft_rules)} SOFT")
        return hard_rules, soft_rules

    def get_rules_for_prompt_injection(self) -> str:
        """
        Get formatted rules for injection into AI prompts.
        This ensures the AI is aware of compliance requirements.
        """
        rules = self.get_active_rules()
        
        if not rules:
            return "No specific compliance rules currently active."
        
        hard_rules, soft_rules = self.categorize_rules()
        
        prompt_section = "COMPLIANCE RULES (MUST BE ENFORCED):\n\n"
        
        if hard_rules:
            prompt_section += "HARD RULES (VIOLATIONS WILL BLOCK CONTENT):\n"
            for i, rule in enumerate(hard_rules, 1):
                prompt_section += f"{i}. {rule.rule_text}\n"
            prompt_section += "\n"
        
        if soft_rules:
            prompt_section += "SOFT RULES (VIOLATIONS WILL BE FLAGGED):\n"
            for i, rule in enumerate(soft_rules, 1):
                prompt_section += f"{i}. {rule.rule_text}\n"
        
        return prompt_section

    def check_violations(self, content: str) -> List[Dict]:
        """
        Check content against all active rules.
        Returns list of violations with severity and context.
        
        Args:
            content: Generated content to check
        
        Returns:
            List of violation dictionaries
        """
        violations = []
        rules = self.get_active_rules()
        
        for rule in rules:
            # Simple keyword/phrase matching for rule enforcement
            # In production, this would use more sophisticated NLP
            violation = self._check_single_rule(content, rule)
            if violation:
                violations.append(violation)
        
        logger.info(f"Found {len(violations)} rule violations")
        return violations

    def _check_single_rule(self, content: str, rule: Rule) -> Dict | None:
        """
        Check content against a single rule.
        Uses simple keyword matching for POC.
        
        In production, this would use:
        - NLP-based semantic matching
        - Regex patterns
        - Custom rule logic
        """
        content_lower = content.lower()
        rule_text_lower = rule.rule_text.lower()
        
        # Extract key phrases from rule (simplified)
        # Look for prohibited terms or required terms
        if "must not" in rule_text_lower or "prohibited" in rule_text_lower:
            # Check for prohibited content
            prohibited_terms = self._extract_prohibited_terms(rule.rule_text)
            for term in prohibited_terms:
                if term.lower() in content_lower:
                    return {
                        "rule_id": rule.id,
                        "rule_text": rule.rule_text,
                        "severity": rule.severity.value,
                        "violated_text": self._extract_context(content, term),
                        "context": f"Prohibited term '{term}' found in content"
                    }
        
        elif "must include" in rule_text_lower or "required" in rule_text_lower:
            # Check for required content
            required_terms = self._extract_required_terms(rule.rule_text)
            for term in required_terms:
                if term.lower() not in content_lower:
                    return {
                        "rule_id": rule.id,
                        "rule_text": rule.rule_text,
                        "severity": rule.severity.value,
                        "violated_text": "",
                        "context": f"Required term '{term}' missing from content"
                    }
        
        return None

    def _extract_prohibited_terms(self, rule_text: str) -> List[str]:
        """Extract prohibited terms from rule text (simplified)"""
        # In production, use proper NLP parsing
        import re
        
        # Look for quoted terms
        quoted = re.findall(r'"([^"]*)"', rule_text)
        if quoted:
            return quoted
        
        # Look for terms after "such as" or "including"
        if "such as" in rule_text.lower():
            parts = rule_text.lower().split("such as")
            if len(parts) > 1:
                terms = parts[1].split(",")
                return [t.strip().strip('"\'') for t in terms]
        
        return []

    def _extract_required_terms(self, rule_text: str) -> List[str]:
        """Extract required terms from rule text (simplified)"""
        import re
        
        # Look for quoted terms
        quoted = re.findall(r'"([^"]*)"', rule_text)
        if quoted:
            return quoted
        
        return []

    def _extract_context(self, content: str, term: str, context_chars: int = 100) -> str:
        """Extract surrounding context for a term in content"""
        content_lower = content.lower()
        term_lower = term.lower()
        
        pos = content_lower.find(term_lower)
        if pos == -1:
            return term
        
        start = max(0, pos - context_chars)
        end = min(len(content), pos + len(term) + context_chars)
        
        context = content[start:end]
        if start > 0:
            context = "..." + context
        if end < len(content):
            context = context + "..."
        
        return context

    def enforce_hard_rules(self, content: str, violations: List[Dict]) -> Tuple[bool, str]:
        """
        Enforce HARD rules - block content if violations exist.
        
        Args:
            content: Generated content
            violations: List of detected violations
        
        Returns:
            Tuple of (is_approved, reason)
        """
        hard_violations = [v for v in violations if v["severity"] == "hard"]
        
        if hard_violations:
            reasons = [f"- {v['rule_text']}: {v['context']}" for v in hard_violations]
            reason = "Content BLOCKED due to HARD rule violations:\n" + "\n".join(reasons)
            logger.warning(f"Content blocked: {len(hard_violations)} HARD violations")
            return False, reason
        
        return True, "No HARD rule violations"

    def annotate_soft_rules(self, violations: List[Dict]) -> str:
        """
        Create annotations for SOFT rule violations.
        Content is approved but flagged.
        """
        soft_violations = [v for v in violations if v["severity"] == "soft"]
        
        if not soft_violations:
            return "No SOFT rule violations"
        
        annotations = ["SOFT RULE VIOLATIONS (Content approved with warnings):"]
        for v in soft_violations:
            annotations.append(f"- {v['rule_text']}: {v['context']}")
        
        return "\n".join(annotations)


def get_rule_engine(db: Session) -> RuleEngine:
    """Factory function to create rule engine instance"""
    return RuleEngine(db)
