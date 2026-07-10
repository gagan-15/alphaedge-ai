from enum import Enum


class TradingSignal(Enum):
    """
    Trading signals returned by the Rule Engine.
    """

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"