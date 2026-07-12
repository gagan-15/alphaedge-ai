"""
Rule Engine for AlphaEdge AI.

This module evaluates indicator outputs and produces
deterministic trading decisions.

Sprint:
    2.21 - Rule Engine Foundation
"""

from typing import Any

from backend.core.logger import logger
from backend.validators.rule_validator import RuleValidator
from backend.models.trading_signal import TradingSignal
from backend.engines.rule_engine.rule_builder import RuleBuilder
from backend.engines.rule_engine.rule_evaluator import RuleEvaluator


class RuleEngine:
    """
    Rule Engine responsible for evaluating
    multiple indicator outputs.

    The Rule Engine does NOT calculate indicators.

    It combines already calculated indicator
    results into a trading decision.
    """

    def __init__(self) -> None:
        """
        Initialize Rule Engine.
        """
        logger.info("RuleEngine initialized.")
        self.rule_builder = RuleBuilder()
        self.rule_evaluator = RuleEvaluator()

    def evaluate(
        self,
        indicator_results: dict[str, Any]
    ) -> TradingSignal:
        """
        Evaluate indicator outputs.
        """

        logger.info("Starting rule evaluation.")

        RuleValidator.validate_indicator_results(
            indicator_results
        )

        rule = self.rule_builder.evaluate(
            indicator_results
        )

        decision = self.rule_evaluator.evaluate(rule)

        logger.info("Rule evaluation completed.")

        return decision