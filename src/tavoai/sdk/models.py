"""Models for the TavoAI SDK."""

from enum import Enum
from typing import Dict, List, Any


class ContentType(Enum):
    """Type of content to evaluate."""
    INPUT = "input"
    OUTPUT = "output"


class PolicyResult:
    """Represents the result of a policy evaluation."""
    
    def __init__(self, allowed: bool, rejection_reasons: List[Dict[str, str]] = None):
        """
        Initialize a PolicyResult object.
        
        Args:
            allowed: Whether the content is allowed by the policy.
            rejection_reasons: List of rejection reasons, each with 'category' and 'reason' fields.
        """
        self.allowed = allowed
        self.rejection_reasons = rejection_reasons or []
    
    def __str__(self) -> str:
        if self.allowed:
            return "Policy evaluation passed"
        
        reason_strs = []
        for reason_obj in self.rejection_reasons:
            category = reason_obj.get("category", "Unknown")
            reason = reason_obj.get("reason", "No reason provided")
            reason_strs.append(f"{category}: {reason}")
        
        return f"Policy evaluation failed: {', '.join(reason_strs)}" 