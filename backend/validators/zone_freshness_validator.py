"""
Zone Freshness Validator for AlphaEdge AI.

Sprint:
    2.27 - Zone Freshness Engine
"""

from pandas import DataFrame

from backend.models.zone import Zone


class ZoneFreshnessValidator:
    """
    Validate inputs for the Zone Freshness Engine.
    """

    @staticmethod
    def validate(
        zone: Zone,
        market_data: DataFrame,
    ) -> None:
        """
        Validate zone and market data.
        """

        if zone is None:
            raise ValueError("Zone cannot be None.")

        if market_data.empty:
            raise ValueError("Market data cannot be empty.")

        if zone.upper_price <= zone.lower_price:
            raise ValueError("Zone upper price must be greater than lower price.")

        if zone.created_index < 0:
            raise ValueError("Zone created_index cannot be negative.")

        if zone.created_index >= len(market_data):
            raise ValueError("Zone created_index is outside market data.")
