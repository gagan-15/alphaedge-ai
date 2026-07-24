"""
Dashboard API Response Models.

Sprint:
    2.61 - Signals Panel
"""

from typing import Any

from pydantic import BaseModel, ConfigDict


class APIResponseModel(BaseModel):
    """
    Base configuration for API response models.
    """

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
    )


class MarketOverviewResponse(APIResponseModel):
    """
    Market overview data returned by the Dashboard API.
    """

    nifty50: float
    nifty_change: float
    sensex: float
    sensex_change: float
    bank_nifty: float
    bank_nifty_change: float
    india_vix: float
    india_vix_change: float


class PortfolioResponse(APIResponseModel):
    """
    Portfolio summary returned by the Dashboard API.
    """

    total_positions: int
    invested_capital: float
    available_capital: float
    total_capital: float


class SignalResponse(APIResponseModel):
    """
    Trading signal returned by the Dashboard API.
    """

    symbol: str
    action: str
    price: float
    confidence: float


class AlertResponse(APIResponseModel):
    """
    Alert returned by the Dashboard API.
    """

    title: str
    message: str
    priority: str
    requires_action: bool


class ScreenerResponse(APIResponseModel):
    """
    Screener result included in the market scanner response.
    """

    opportunities: list[Any]


class MarketScannerResponse(APIResponseModel):
    """
    Market scanner summary returned by the Dashboard API.
    """

    scanned_symbols: int
    screener_result: ScreenerResponse


class BacktestResponse(APIResponseModel):
    """
    Backtest summary returned by the Dashboard API.
    """

    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float


class AIExplanationResponse(APIResponseModel):
    """
    AI explanation returned by the Dashboard API.
    """

    decision: str
    reasons: tuple[str, ...]
    confidence_score: float
    summary: str


class DashboardResponse(APIResponseModel):
    """
    Complete response returned by the Dashboard API.
    """

    market: MarketOverviewResponse
    portfolio: PortfolioResponse
    signals: tuple[SignalResponse, ...]
    alerts: tuple[AlertResponse, ...]
    scanner: MarketScannerResponse
    backtest: BacktestResponse
    ai_explanation: AIExplanationResponse
