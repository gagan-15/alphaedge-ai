"""
AI Explanation Result model.

Sprint:
    2.42 - AI Explanation Engine
"""

from dataclasses import dataclass

from backend.models.ai_explanation.ai_explanation_decision import (
    AIExplanationDecision,
)


@dataclass(frozen=True)
class AIExplanationResult:
    """
    Represents a structured explanation of a
    rule-based trading decision.
    """

    decision: AIExplanationDecision

    reasons: tuple[str, ...]

    confidence_score: float

    summary: str
