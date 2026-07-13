"""
File Name:
    main.py

Purpose:
    Entry point of AlphaEdge AI.

Description:
    This file starts the AlphaEdge AI application.
    It initializes the Market Data Service, downloads
    historical stock data, and displays the results.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

# --------------------------------------------------------
# Import Required Services
# --------------------------------------------------------

from backend.services.market_data.market_data_service import MarketDataService
from backend.services.indicator.indicator_service import IndicatorService
from backend.config.settings import (
    APP_NAME,
    VERSION,
    DEFAULT_SYMBOL,
    DEFAULT_PERIOD,
    DEFAULT_INTERVAL,
)
from backend.core.logger import logger


def main():
    """
    Main entry point of the AlphaEdge AI application.
    """
    try:
        print("=" * 60)
        logger.info(f"Welcome to {APP_NAME} (v{VERSION})")
        print("=" * 60)

        # Create an instance of the Market Data Service.
        # This service is responsible for retrieving
        # historical stock market data.

        market_service = MarketDataService()

        # Request one year of daily historical data
        # for Tata Consultancy Services (TCS).
        stock_data = market_service.get_stock_data(
            symbol=DEFAULT_SYMBOL,
            period=DEFAULT_PERIOD,
            interval=DEFAULT_INTERVAL,
        )

        indicator_service = IndicatorService()

        result = indicator_service.calculate_ema(stock_data)

        # Display the first five rows of the downloaded data.
        print(result.head())

    except ValueError as error:
        logger.error(error)
        print("\n❌ Error")
        print(error)


# Execute the application only when this file
# is run directly.
if __name__ == "__main__":
    main()
