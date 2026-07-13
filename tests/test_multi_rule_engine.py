import pytest

from backend.engines.rule_engine.multi_rule_engine import MultiRuleEngine
from backend.models.rule import Rule
from backend.models.trading_signal import TradingSignal


class TestMultiRuleEngine:

    def setup_method(self):
        self.engine = MultiRuleEngine()

    def test_returns_buy_when_buy_is_majority(self):
        rules = [
            Rule("RSI", True, TradingSignal.BUY, ""),
            Rule("MACD", True, TradingSignal.BUY, ""),
            Rule("ADX", True, TradingSignal.SELL, ""),
        ]

        result = self.engine.evaluate(rules)

        assert result.signal == TradingSignal.BUY

    def test_returns_sell_when_sell_is_majority(self):
        rules = [
            Rule("RSI", True, TradingSignal.SELL, ""),
            Rule("MACD", True, TradingSignal.SELL, ""),
            Rule("ADX", True, TradingSignal.BUY, ""),
        ]

        result = self.engine.evaluate(rules)

        assert result.signal == TradingSignal.SELL

    def test_returns_hold_when_hold_is_majority(self):
        rules = [
            Rule("RSI", True, TradingSignal.HOLD, ""),
            Rule("MACD", True, TradingSignal.HOLD, ""),
            Rule("ADX", True, TradingSignal.BUY, ""),
        ]

        result = self.engine.evaluate(rules)

        assert result.signal == TradingSignal.HOLD

    def test_none_rules_raises_value_error(self):

        with pytest.raises(ValueError):
            self.engine.evaluate(None)

    def test_empty_rules_raises_value_error(self):

        with pytest.raises(ValueError):
            self.engine.evaluate([])

    def test_invalid_rule_type_raises_type_error(self):

        with pytest.raises(TypeError):
            self.engine.evaluate(["invalid"])
