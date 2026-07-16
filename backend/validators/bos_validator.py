"""
Break of Structure Validator.

Sprint:
    2.29 - Break of Structure Engine
"""

from pandas import DataFrame

from backend.config.bos_config import BOSConfig


class BOSValidator:
    """
    Validate Break of Structure Engine inputs.
    """

    REQUIRED_COLUMNS = (
        "Open",
        "High",
        "Low",
        "Close",
    )

    @classmethod
    def validate(
        cls,
        market_data: DataFrame,
        config: BOSConfig,
    ) -> None:
        """
        Validate inputs.
        """

        if not isinstance(market_data, DataFrame):
            raise TypeError(
                "market_data must be a pandas DataFrame."
            )

        if market_data.empty:
            raise ValueError(
                "market_data cannot be empty."
            )

        missing = [
            column
            for column in cls.REQUIRED_COLUMNS
            if column not in market_data.columns
        ]

        if missing:
            raise ValueError(
                "Missing required columns: "
                + ", ".join(missing)
            )

        if not isinstance(config, BOSConfig):
            raise TypeError(
                "config must be a BOSConfig."
            )

        if config.swing_left_bars < 1:
            raise ValueError(
                "swing_left_bars must be greater than zero."
            )

        if config.swing_right_bars < 1:
            raise ValueError(
                "swing_right_bars must be greater than zero."
            )

        if config.break_buffer_value < 0:
            raise ValueError(
                "break_buffer_value cannot be negative."
            )

        if len(market_data) < (
            config.swing_left_bars
            + config.swing_right_bars
            + 1
        ):
            raise ValueError(
                "Insufficient market data for swing detection."
            )