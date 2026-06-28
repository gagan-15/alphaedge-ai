from backend.data_providers.yahoo.yahoo_provider import YahooProvider
from backend.validators.market_data_validator import MarketDataValidator


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
    
        # Return validated market data.

        return data