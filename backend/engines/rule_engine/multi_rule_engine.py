"""
Multi Rule Engine for AlphaEdge AI.

Sprint:
    2.24 - Multi Rule Engine
"""

from collections import Counter

from backend.core.logger import logger
from backend.models.rule import Rule
from backend.models.trading_signal import TradingSignal
from backend.validators.multi_rule_validator import MultiRuleValidator


class MultiRuleEngine:
    """
    Combines multiple evaluated trading rules into
    one final trading decision.
    """

    def evaluate(self, rules: list[Rule]) -> Rule:
        """
        Evaluate multiple rules and return a single
        trading signal.

        Args:
            rules:
                List of evaluated Rule objects.

        Returns:
            Rule
        """

        logger.info("Starting Multi Rule Engine.")

        MultiRuleValidator.validate_rules(rules)

        signal_counts = self._count_signals(rules)

        decision = self._select_final_signal(signal_counts)

        logger.info("Multi Rule decision: %s", decision.name)

        return Rule(
            name="Multi Rule Decision",
            passed=True,
            signal=decision,
            reason="Combined decision from multiple rules.",
        )

    def _count_signals(self, rules: list[Rule]) -> Counter:
        """
        Count occurrences of each trading signal.
        """

        return Counter(rule.signal for rule in rules)

    def _select_final_signal(self, signal_counts: Counter) -> TradingSignal:
        """
        Select the trading signal with the highest
        occurrence.
        """

        if not signal_counts:
            return TradingSignal.HOLD

        return signal_counts.most_common(1)[0][0]
