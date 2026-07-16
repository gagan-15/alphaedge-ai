"""
Market Structure Validator.

Sprint:
    2.30 - Market Structure Foundation
"""

from pandas import DataFrame


class MarketStructureValidator:
    """
    Validate Market Structure inputs.
    """

    REQUIRED_COLUMNS = (
        "Open",
        "High",
        "Low",
        "Close",
    )

    @classmethod
    def validate_market_data(
        cls,
        market_data: DataFrame,
    ) -> None:

        if not isinstance(
            market_data,
            DataFrame,
        ):
            raise TypeError("market_data must be a pandas DataFrame.")

        if market_data.empty:
            raise ValueError("market_data cannot be empty.")

        missing = [
            column
            for column in cls.REQUIRED_COLUMNS
            if column not in market_data.columns
        ]

        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        if len(market_data) < 5:
            raise ValueError("Insufficient market data.")
