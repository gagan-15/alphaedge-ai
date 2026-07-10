"""
Unit tests for the Rule Engine.

Sprint:
    2.21 - Rule Engine Foundation
"""

import pytest

from backend.engines.rule_engine.rule_engine import RuleEngine
from backend.models.trading_signal import TradingSignal


class TestRuleEngine:
    """
    Unit tests for RuleEngine.
    """

    def setup_method(self):
        """
        Create a fresh RuleEngine instance
        before each test.
        """
        self.rule_engine = RuleEngine()

    def test_evaluate_returns_buy(self):
        """
        RuleEngine should return BUY
        when RSI is greater than 50.
        """

        indicator_results = {
            "rsi": 55
        }

        decision = self.rule_engine.evaluate(
            indicator_results
        )

        assert decision == TradingSignal.BUY


    def test_evaluate_returns_sell(self):
        """
        RuleEngine should return SELL
        when RSI is less than 50.
        """

        indicator_results = {
            "rsi": 45
        }

        decision = self.rule_engine.evaluate(
            indicator_results
        )

        assert decision == TradingSignal.SELL

    def test_evaluate_none_input(self):
        """
        RuleEngine should raise ValueError
        when indicator results are None.
        """

        with pytest.raises(ValueError):
            self.rule_engine.evaluate(None)

    def test_evaluate_empty_dictionary(self):
        """
        RuleEngine should raise ValueError
        for an empty dictionary.
        """

        with pytest.raises(ValueError):
            self.rule_engine.evaluate({})

    def test_evaluate_invalid_input_type(self):
        """
        RuleEngine should raise TypeError
        when input is not a dictionary.
        """

        with pytest.raises(TypeError):
            self.rule_engine.evaluate([])