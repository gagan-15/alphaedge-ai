"""
Unit tests for Rule Builder.

Sprint:
    2.22 - Rule Builder
"""

from backend.engines.rule_engine.rule_builder import RuleBuilder
from backend.models.trading_signal import TradingSignal


class TestRuleBuilder:

    def setup_method(self):
        self.rule_builder = RuleBuilder()

    def test_returns_buy(self):
        indicator_results = {
            "rsi": 55
        }

        decision = self.rule_builder.evaluate(
            indicator_results
        )

        assert decision == TradingSignal.BUY

    def test_returns_sell(self):
        indicator_results = {
            "rsi": 45
        }

        decision = self.rule_builder.evaluate(
            indicator_results
        )

        assert decision == TradingSignal.SELL

    def test_returns_hold(self):
        indicator_results = {
            "rsi": 50
        }

        decision = self.rule_builder.evaluate(
            indicator_results
        )

        assert decision == TradingSignal.HOLD