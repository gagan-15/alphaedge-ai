"""
Zone validator for AlphaEdge AI.

Sprint:
    2.25 - Demand & Supply Foundation
"""

from backend.models.zone import Zone


class ZoneValidator:
    """
    Validates Zone objects.
    """

    @staticmethod
    def validate_zone(
        zone: Zone
    ) -> None:
        """
        Validate a Zone.

        Args:
            zone:
                Zone to validate.

        Raises:
            TypeError:
                If zone is invalid.

            ValueError:
                If zone values are invalid.
        """

        if not isinstance(zone, Zone):
            raise TypeError(
                "zone must be a Zone."
            )

        if zone.upper_price <= 0:
            raise ValueError(
                "upper_price must be greater than zero."
            )

        if zone.lower_price <= 0:
            raise ValueError(
                "lower_price must be greater than zero."
            )

        if zone.upper_price <= zone.lower_price:
            raise ValueError(
                "upper_price must be greater than lower_price."
            )