"""
Unit tests for Rule Evaluator.

Sprint:
    2.23 - Rule Evaluator
"""

from backend.engines.rule_engine.rule_evaluator import RuleEvaluator
from backend.models.rule import Rule
from backend.models.trading_signal import TradingSignal
import pytest


class TestRuleEvaluator:

    def setup_method(self):
        self.rule_evaluator = RuleEvaluator()

    def test_returns_buy_signal(self):
        rule = Rule(
            name="RSI Rule",
            passed=True,
            signal=TradingSignal.BUY,
            reason="RSI > 50"
        )

        decision = self.rule_evaluator.evaluate(rule)

        assert decision == TradingSignal.BUY

    def test_returns_sell_signal(self):
        rule = Rule(
            name="RSI Rule",
            passed=True,
            signal=TradingSignal.SELL,
            reason="RSI < 50"
        )

        decision = self.rule_evaluator.evaluate(rule)

        assert decision == TradingSignal.SELL

    def test_returns_hold_signal(self):
        rule = Rule(
            name="RSI Rule",
            passed=False,
            signal=TradingSignal.HOLD,
            reason="RSI = 50"
        )

        decision = self.rule_evaluator.evaluate(rule)

        assert decision == TradingSignal.HOLD


    def test_rule_cannot_be_none(self):
     with pytest.raises(ValueError):
      self.rule_evaluator.evaluate(None)