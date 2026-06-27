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


def main():
    """
    Main entry point of the AlphaEdge AI application.
    """

    print("=" * 60)
    print("🚀 Welcome to AlphaEdge AI")
    print("=" * 60)

    # Create an instance of the Market Data Service.
    # This service is responsible for retrieving
    # historical stock market data.
    market_service = MarketDataService()

    # Request one year of daily historical data
    # for Tata Consultancy Services (TCS).
    stock_data = market_service.get_stock_data(
        symbol="TCS.NS",
        period="1y",
        interval="1d",
    )

    # Display the first five rows of the downloaded data.
    print(stock_data.head())


# Execute the application only when this file
# is run directly.
if __name__ == "__main__":
    main()