"""
Market Overview Result.
"""

from pydantic import BaseModel


class MarketOverviewResult(BaseModel):
    """
    Market overview information.
    """

    nifty50: float
    nifty_change: float

    sensex: float
    sensex_change: float

    bank_nifty: float
    bank_nifty_change: float

    india_vix: float
    india_vix_change: float
