"""
Demand & Supply Engine for AlphaEdge AI.

Sprint:
    2.25 - Demand & Supply Foundation
"""

from backend.core.logger import logger
from backend.models.zone import Zone
from backend.validators.zone_validator import ZoneValidator
from pandas import DataFrame

class DemandSupplyEngine:
    """
    Foundation for all future Demand & Supply analysis.
    """

    def validate(
        self,
        zone: Zone
    ) -> Zone:
        """
        Validate a zone.

        Args:
            zone:
                Zone to validate.

        Returns:
            Zone
        """

        logger.info(
            "Starting zone validation."
        )

        ZoneValidator.validate_zone(
            zone
        )

        logger.info(
            "Zone validation completed."
        )

        return zone
    
    

    def prepare_data(
        self,
        market_data: DataFrame
    ) -> DataFrame:
        """
        Prepare market data for future
        Demand & Supply analysis.

        Args:
            market_data:
                Validated OHLCV market data.

        Returns:
            DataFrame
        """

        logger.info(
            "Preparing market data for Demand & Supply analysis."
        )

        return market_data.copy()