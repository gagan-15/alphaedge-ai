"""
AI Explanation validator.

Sprint:
    2.42 - AI Explanation Engine
"""

from backend.config.ai_explanation_config import (
    AIExplanationConfig,
)


class AIExplanationValidator:
    """
    Validator for the AI Explanation Engine.
    """

    @staticmethod
    def validate_config(
        config: AIExplanationConfig,
    ) -> None:
        """
        Validate AI Explanation configuration.
        """

        if config.maximum_reasons <= 0:
            raise ValueError("Maximum reasons must be greater than zero.")
