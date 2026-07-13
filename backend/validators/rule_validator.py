"""
Rule Validator for AlphaEdge AI.

This module validates inputs passed to the Rule Engine.

Sprint:
    2.21 - Rule Engine Foundation
"""

from typing import Any


class RuleValidator:
    """
    Validator for Rule Engine inputs.
    """

    @staticmethod
    def validate_indicator_results(indicator_results: dict[str, Any]) -> None:
        """
        Validate indicator results.

        Args:
            indicator_results:
                Dictionary containing indicator outputs.

        Raises:
            ValueError:
                If indicator results are None or empty.

            TypeError:
                If indicator results are not a dictionary.
        """

        if indicator_results is None:
            raise ValueError("Indicator results cannot be None.")

        if not isinstance(indicator_results, dict):
            raise TypeError("Indicator results must be a dictionary.")

        if not indicator_results:
            raise ValueError("Indicator results cannot be empty.")

        if "rsi" not in indicator_results:
            raise ValueError("RSI result is required.")
