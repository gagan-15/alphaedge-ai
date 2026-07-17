"""
Market Scanner Engine.

Sprint:
    2.40 - Market Scanner Engine
"""

from backend.config.market_scanner_config import (
    MarketScannerConfig,
)
from backend.models.market_scanner.market_scanner_result import (
    MarketScannerResult,
)
from backend.models.screener.screener_result import (
    ScreenerResult,
)
from backend.validators.market_scanner_validator import (
    MarketScannerValidator,
)


class MarketScannerEngine:
    """
    Coordinates market scanning using the
    existing AlphaEdge AI trading pipeline.
    """

    def __init__(
        self,
        config: MarketScannerConfig,
    ) -> None:
        """
        Initialize the Market Scanner Engine.
        """
        MarketScannerValidator.validate_config(config)

        self._config = config

    def scan(
        self,
        symbols: list[str],
        screener_result: ScreenerResult,
    ) -> MarketScannerResult:
        """
        Produce a MarketScannerResult for the
        supplied symbols.
        """

        symbols_to_scan = symbols[: self._config.maximum_symbols]

        return MarketScannerResult(
            scanned_symbols=len(symbols_to_scan),
            screener_result=screener_result,
        )
