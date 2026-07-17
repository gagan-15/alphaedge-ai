"""
AI Explanation configuration.

Sprint:
    2.42 - AI Explanation Engine
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AIExplanationConfig:
    """
    Configuration for the AI Explanation Engine.
    """

    maximum_reasons: int = 5

    include_confidence_score: bool = True
