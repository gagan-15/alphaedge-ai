"""
Zone Strength Validator.

Sprint:
    2.28 - Zone Strength Engine
"""

from pandas import DataFrame

from backend.models.zone import Zone


class ZoneStrengthValidator:
    """
    Validate Zone Strength Engine inputs.
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
        zone: Zone,
        market_data: DataFrame,
    ) -> None:
        """
        Validate inputs.
        """

        if not isinstance(zone, Zone):
            raise TypeError("zone must be a Zone.")

        if not isinstance(market_data, DataFrame):
            raise TypeError("market_data must be a pandas DataFrame.")

        if market_data.empty:
            raise ValueError("market_data cannot be empty.")

        missing = [
            column
            for column in cls.REQUIRED_COLUMNS
            if column not in market_data.columns
        ]

        if missing:
            raise ValueError("Missing required columns: " + ", ".join(missing))

        if zone.created_index >= len(market_data):
            raise ValueError("Zone creation index is outside market data.")
