from backend.data_providers.yahoo.yahoo_provider import YahooProvider
from backend.validators.market_data_validator import MarketDataValidator
from backend.core.logger import logger


class MarketDataService:
    """
    Service responsible for fetching market data.
    """

    def __init__(self):
        self.provider = YahooProvider()

    def get_stock_data(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
    ):
        logger.info(f"Downloading market data for {symbol}")

        """
        Get stock market data.
        """

        # Download market data from the provider.
        data = self.provider.download_stock_data(
            symbol=symbol,
            period=period,
            interval=interval,
        )

        # Validate the downloaded market data.
        MarketDataValidator.validate(data)

        logger.info("Market data validation completed successfully.")

        # Return validated market data.

        return data
