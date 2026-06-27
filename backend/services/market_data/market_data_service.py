from backend.data_providers.yahoo.yahoo_provider import YahooProvider


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

        return self.provider.download_stock_data(
            symbol=symbol,
            period=period,
            interval=interval,
        )