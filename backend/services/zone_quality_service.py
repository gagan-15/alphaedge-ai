"""
Zone Quality Service.

Sprint:
    2.67 - Zone Quality Scoring
"""

from backend.models.zone_scoring.zone_quality import (
    ZoneQuality,
)


class ZoneQualityService:
    """
    Calculates overall zone quality.
    """

    @staticmethod
    def calculate(
        base_score: float,
        leg_in_score: float,
        leg_out_score: float,
        freshness_score: float,
    ) -> ZoneQuality:

        total_score = round(
            (
                base_score
                + leg_in_score
                + leg_out_score
                + freshness_score
            )
            / 4,
            2,
        )

        return ZoneQuality(
            base_score=base_score,
            leg_in_score=leg_in_score,
            leg_out_score=leg_out_score,
            freshness_score=freshness_score,
            total_score=total_score,
        )
