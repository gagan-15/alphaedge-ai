from pandas import DataFrame

from backend.core.logger import logger
from backend.data_providers.base_market_data_provider import BaseMarketDataProvider
from backend.data_providers.yahoo.yahoo_provider import YahooProvider
from backend.validators.market_data_validator import MarketDataValidator


class MarketDataService:
    """
    Service responsible for fetching market data.
    """

    def __init__(
        self,
        provider: BaseMarketDataProvider | None = None,
    ) -> None:
        """
        Initialize the service with a market data provider.

        Args:
            provider:
                Optional provider implementation. Yahoo Finance is used
                by default during development.
        """

        self._provider = provider or YahooProvider()

    def get_stock_data(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> DataFrame:
        """
        Get stock market data.
        """

        logger.info(
            "Downloading market data for %s.",
            symbol,
        )

        data = self._provider.download_stock_data(
            symbol=symbol,
            period=period,
            interval=interval,
        )

        # Validate the downloaded market data.
        MarketDataValidator.validate(data)

        logger.info("Market data validation completed successfully.")

        return data
