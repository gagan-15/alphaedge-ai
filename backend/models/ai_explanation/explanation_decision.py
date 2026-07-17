"""
Explanation Decision.

Sprint:
    2.42 - AI Explanation Engine
"""

from enum import Enum


class ExplanationDecision(str, Enum):
    """
    Supported explanation decisions.
    """

    BUY = "BUY"

    SELL = "SELL"

    HOLD = "HOLD"

    WAIT = "WAIT"
