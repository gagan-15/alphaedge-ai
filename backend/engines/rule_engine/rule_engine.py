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
from backend.config.settings import RSI_NEUTRAL_LEVEL
from backend.models.trading_signal import TradingSignal


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

    def evaluate(
    self,
    indicator_results: dict[str, Any]
) -> TradingSignal:
        """
        Evaluate indicator outputs.

        Args:
            indicator_results:
                Dictionary containing
                calculated indicator outputs.

        Returns:
            str:
                BUY, SELL or HOLD.
        """

        logger.info("Starting rule evaluation.")

        RuleValidator.validate_indicator_results(
            indicator_results
        )

        rsi = indicator_results["rsi"]

        if rsi > RSI_NEUTRAL_LEVEL:
            logger.info("Trading decision: BUY")
            return TradingSignal.BUY
        
        if rsi < RSI_NEUTRAL_LEVEL:
            logger.info("Trading decision: SELL")
            return TradingSignal.SELL

        logger.info("Trading decision: HOLD")
        return TradingSignal.HOLD