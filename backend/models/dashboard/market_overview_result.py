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
    nifty_available: bool = False

    sensex: float
    sensex_change: float
    sensex_available: bool = False

    bank_nifty: float
    bank_nifty_change: float
    bank_nifty_available: bool = False

    india_vix: float
    india_vix_change: float
    india_vix_available: bool = False
    advancing: int = 0
    declining: int = 0
    unchanged: int = 0
    total_symbols: int = 0
    processed_symbols: int = 0
    source: str = ""
    data_status: str = "delayed"
    updated_at: str = ""
