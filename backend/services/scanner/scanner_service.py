"""
Scanner Service.

Sprint:
    2.64 - Scanner Results Foundation
"""

from concurrent.futures import ThreadPoolExecutor, as_completed

from backend.config.market_scanner_config import (
    MarketScannerConfig,
)
from backend.config.scanner_config import (
    ScannerConfig,
)
from backend.config.screener_config import ScreenerConfig
from backend.core.logger import logger
from backend.engines.market_scanner.market_scanner_engine import (
    MarketScannerEngine,
)
from backend.engines.screener_engine.screener_engine import (
    ScreenerEngine,
)
from backend.models.market_scanner.market_scanner_result import (
    MarketScannerResult,
)
from backend.models.screener.screened_opportunity import (
    ScreenedOpportunity,
)
from backend.services.market_data.market_data_service import MarketDataService
from backend.services.scanner.market_opportunity_service import (
    MarketOpportunityService,
)
from backend.validators.scanner_validator import (
    ScannerValidator,
)
from backend.services.scanner.universe_service import (
    UniverseName,
    UniverseService,
)


class ScannerService:
    """
    Provides scanner data.
    """

    def __init__(
        self,
        config: ScannerConfig | None = None,
        opportunity_service: MarketOpportunityService | None = None,
        universe_service: UniverseService | None = None,
    ) -> None:
        """
        Initialize the Scanner Service.
        """

        self._config = config or ScannerConfig()

        ScannerValidator.validate_config(
            self._config,
        )

        self._market_scanner_engine = MarketScannerEngine(
            MarketScannerConfig(),
        )
        self._screener_engine = ScreenerEngine(
            ScreenerConfig(),
        )
        self._opportunity_service = opportunity_service or MarketOpportunityService(
            market_data_service=MarketDataService(),
            config=self._config,
        )
        self._universe_service = universe_service or UniverseService()

    def get_scanner(
        self,
        universe: UniverseName = "nse500",
        supplied_symbols: list[str] | None = None,
    ) -> MarketScannerResult:
        """
        Return the current scanner data.

        Each symbol is isolated so one provider or analysis failure does not
        stop the complete scan.
        """

        opportunities: list[ScreenedOpportunity] = []

        symbols = self._universe_service.get_symbols(
            universe,
            supplied_symbols,
        )

        def analyze(symbol: str) -> ScreenedOpportunity | None:
            try:
                return self._opportunity_service.analyze(symbol)
            except Exception:
                logger.exception(
                    "Scanner analysis failed for %s.",
                    symbol,
                )
                return None

        with ThreadPoolExecutor(
            max_workers=min(self._config.scan_concurrency, max(1, len(symbols))),
            thread_name_prefix="alphaedge-scanner",
        ) as executor:
            futures = {executor.submit(analyze, symbol): symbol for symbol in symbols}
            for future in as_completed(futures):
                opportunity = future.result()
                if opportunity is not None:
                    opportunities.append(opportunity)

        screener_result = self._screener_engine.screen(
            opportunities,
        )

        return self._market_scanner_engine.scan(
            symbols=symbols,
            screener_result=screener_result,
        )
