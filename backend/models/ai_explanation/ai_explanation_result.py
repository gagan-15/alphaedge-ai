"""
AI Explanation Result model.

Sprint:
    2.42 - AI Explanation Engine
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AIExplanationResult:
    """
    Represents a structured explanation of a
    rule-based trading decision.
    """

    from backend.models.ai_explanation.explanation_decision import (
        ExplanationDecision,
    )

    decision: ExplanationDecision

    reasons: tuple[str, ...]

    confidence_score: float

    summary: str
