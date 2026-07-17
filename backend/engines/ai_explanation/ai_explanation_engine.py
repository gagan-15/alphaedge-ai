"""
AI Explanation Engine.

Sprint:
    2.42 - AI Explanation Engine
"""

from backend.config.ai_explanation_config import (
    AIExplanationConfig,
)
from backend.models.ai_explanation.ai_explanation_result import (
    AIExplanationResult,
)
from backend.models.ai_explanation.explanation_decision import (
    ExplanationDecision,
)
from backend.validators.ai_explanation_validator import (
    AIExplanationValidator,
)


class AIExplanationEngine:
    """
    Produces structured explanations for
    trading decisions.
    """

    def __init__(
        self,
        config: AIExplanationConfig,
    ) -> None:
        """
        Initialize the AI Explanation Engine.
        """
        AIExplanationValidator.validate_config(config)

        self._config = config

    def explain(
        self,
        decision: ExplanationDecision,
        reasons: list[str],
        confidence_score: float,
    ) -> AIExplanationResult:
        """
        Produce an AIExplanationResult.
        """

        selected_reasons = tuple(reasons[: self._config.maximum_reasons])

        return AIExplanationResult(
            decision=decision,
            reasons=selected_reasons,
            confidence_score=(
                confidence_score if self._config.include_confidence_score else 0.0
            ),
            summary=selected_reasons[0] if selected_reasons else "",
        )
