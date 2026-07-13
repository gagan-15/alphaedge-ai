"""
Rule Evaluator for AlphaEdge AI.

Sprint:
    2.23 - Rule Evaluator
"""

from backend.models.rule import Rule
from backend.models.trading_signal import TradingSignal
from backend.core.logger import logger


class RuleEvaluator:
    """
    Evaluates Rule objects and returns
    the final trading signal.
    """

    def evaluate(self, rule: Rule) -> TradingSignal:
        """
        Evaluate a Rule and return
        the trading signal.
        """
        if rule is None:
            raise ValueError("Rule cannot be None.")

        logger.info("Starting Rule Evaluator.")

        decision = rule.signal

        logger.info("Rule evaluated: %s", rule.name)

        return decision
