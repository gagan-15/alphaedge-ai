"""
Rule Builder for AlphaEdge AI.

Sprint:
    2.22 - Rule Builder
"""

from typing import Any

from backend.config.settings import RSI_NEUTRAL_LEVEL
from backend.models.trading_signal import TradingSignal
from backend.models.rule import Rule
from backend.core.logger import logger


class RuleBuilder:
    """
    Builds and evaluates trading rules.
    """

    def evaluate(
        self,
        indicator_results: dict[str, Any]
    ) -> TradingSignal:
        """
        Evaluate trading rules.

        Args:
            indicator_results:
                Dictionary containing indicator outputs.

        Returns:
            TradingSignal
        """
        logger.info("Starting Rule Builder evaluation.")

        rsi = indicator_results["rsi"]

        rule = self._evaluate_rsi_rule(rsi)

        logger.info("RSI rule evaluated successfully.")

        logger.info(
                "Trading decision: %s",
                rule.signal.name
            )

        return rule.signal
    
    def _evaluate_rsi_rule(
        self,
        rsi: float
    ) -> Rule:
        """
        Evaluate the RSI trading rule.
        """

        if rsi > RSI_NEUTRAL_LEVEL:
           return Rule(
                name="RSI Rule",
                passed=True,
                signal=TradingSignal.BUY,
                reason="RSI is above the neutral level."
            )

        if rsi < RSI_NEUTRAL_LEVEL:
            return Rule(
                name="RSI Rule",
                passed=True,
                signal=TradingSignal.SELL,
                reason="RSI is below the neutral level."
            )

        return Rule(
            name="RSI Rule",
            passed=False,
            signal=TradingSignal.HOLD,
            reason="RSI is at the neutral level."
        )
                
    def _evaluate_macd_rule(
    self,
    indicator_results: dict[str, Any]
) -> bool:
        """
        Placeholder for MACD rule.
        """

        return True