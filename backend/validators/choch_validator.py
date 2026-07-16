"""
Validator for the Change of Character (CHoCH) Engine.

Sprint:
    2.30 - Change of Character Engine
"""

from pandas import DataFrame

from backend.config.choch_config import CHoCHConfig


class CHoCHValidator:
    """
    Validate inputs for the CHoCH Engine.
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
        """
        Validate market data.
        """

        if not isinstance(
            market_data,
            DataFrame,
        ):
            raise TypeError("market_data must be a pandas DataFrame.")

        if market_data.empty:
            raise ValueError("market_data cannot be empty.")

        missing_columns = [
            column
            for column in cls.REQUIRED_COLUMNS
            if column not in market_data.columns
        ]

        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        if len(market_data) < 5:
            raise ValueError("Insufficient market data.")

    @staticmethod
    def validate_config(
        config: CHoCHConfig,
    ) -> None:
        """
        Validate CHoCH configuration.
        """

        if config.minimum_structure_points < 2:
            raise ValueError("minimum_structure_points must be at least 2.")

        if config.break_buffer_value < 0:
            raise ValueError("break_buffer_value cannot be negative.")

        if config.break_buffer_type not in (
            "percentage",
            "points",
        ):
            raise ValueError("Unsupported break_buffer_type.")

        if config.confirmation_source not in (
            "close",
            "high",
            "low",
        ):
            raise ValueError("Unsupported confirmation_source.")
