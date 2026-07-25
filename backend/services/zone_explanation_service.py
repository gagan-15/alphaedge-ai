"""Build trader-friendly, evidence-based zone explanations."""

from dataclasses import dataclass

from backend.models.zone import Zone
from backend.models.zone_scoring.zone_score import ZoneScore


@dataclass(frozen=True)
class ZoneExplanationFactor:
    """One independently rendered zone-quality factor."""

    key: str
    title: str
    score: float
    sentiment: str
    summary: str
    recommendation: str
    weight: float


@dataclass(frozen=True)
class ZoneExplanation:
    """Complete explanation assembled from available factors."""

    overall_score: float
    rating: int
    label: str
    summary: str
    positive_factors: tuple[ZoneExplanationFactor, ...]
    negative_factors: tuple[ZoneExplanationFactor, ...]
    educational_insight: str


class ZoneExplanationService:
    """Create explanations without presenting quality as probability."""

    @staticmethod
    def build(zone: Zone, score: ZoneScore) -> ZoneExplanation:
        factors = (
            ZoneExplanationService._freshness(zone),
            ZoneExplanationService._departure(score),
            ZoneExplanationService._touches(zone, score),
            ZoneExplanationService._confluence(zone, score),
        )
        positive = tuple(factor for factor in factors if factor.sentiment == "POSITIVE")
        negative = tuple(factor for factor in factors if factor.sentiment == "NEGATIVE")
        overall = round(score.total_score, 1)
        label = ZoneExplanationService._label(overall)
        zone_name = zone.zone_type.value.lower()

        strongest = max(factors, key=lambda factor: factor.score)
        weakest = min(factors, key=lambda factor: factor.score)
        summary = (
            f"This {zone_name} zone has {label.lower()} rule-based quality. "
            f"Its strongest observed factor is {strongest.title.lower()}. "
            f"The main limitation is {weakest.title.lower()}. "
            "The score ranks detected zones; it does not predict that price "
            "will react or that a trade will be profitable."
        )

        return ZoneExplanation(
            overall_score=overall,
            rating=max(1, min(5, round(overall / 20))),
            label=f"{label} {zone.zone_type.value.title()} Zone",
            summary=summary,
            positive_factors=positive,
            negative_factors=negative,
            educational_insight=(
                "Zone quality is stronger when price leaves a compact area "
                "decisively and returns fewer times. Always review market "
                "structure, invalidation and risk before using a zone."
            ),
        )

    @staticmethod
    def _freshness(zone: Zone) -> ZoneExplanationFactor:
        if zone.is_fresh:
            return ZoneExplanationFactor(
                key="freshness",
                title="Fresh zone",
                score=100.0,
                sentiment="POSITIVE",
                summary="Price has not revisited this zone after the departure window.",
                recommendation="Monitor the first return and wait for confirmation.",
                weight=30.0,
            )
        return ZoneExplanationFactor(
            key="freshness",
            title="Zone has been revisited",
            score=0.0,
            sentiment="NEGATIVE",
            summary=f"Price intersected this area {zone.touch_count} later time(s).",
            recommendation="Treat repeated tests as reduced zone quality.",
            weight=30.0,
        )

    @staticmethod
    def _departure(score: ZoneScore) -> ZoneExplanationFactor:
        normalized = round(score.strength_score / 35.0 * 100.0, 1)
        positive = normalized >= 60
        return ZoneExplanationFactor(
            key="departure",
            title="Strong price departure" if positive else "Limited price departure",
            score=normalized,
            sentiment="POSITIVE" if positive else "NEGATIVE",
            summary=(
                "Price moved decisively away relative to the width of the zone."
                if positive
                else "The move away was modest relative to the width of the zone."
            ),
            recommendation=(
                "Confirm that momentum remains present on the selected timeframe."
                if positive
                else "Prefer zones with a clearer, faster move away from the base."
            ),
            weight=35.0,
        )

    @staticmethod
    def _touches(zone: Zone, score: ZoneScore) -> ZoneExplanationFactor:
        normalized = round(score.touch_score / 20.0 * 100.0, 1)
        positive = zone.touch_count <= 1
        return ZoneExplanationFactor(
            key="touches",
            title="Few retests" if positive else "Multiple retests",
            score=normalized,
            sentiment="POSITIVE" if positive else "NEGATIVE",
            summary=f"{zone.touch_count} later zone intersection(s) were detected.",
            recommendation=(
                "Check the reaction quality on the next visit."
                if positive
                else "Repeated testing can weaken the usefulness of the area."
            ),
            weight=20.0,
        )

    @staticmethod
    def _confluence(zone: Zone, score: ZoneScore) -> ZoneExplanationFactor:
        normalized = round(score.merge_bonus / 15.0 * 100.0, 1)
        positive = zone.merged_count > 1
        return ZoneExplanationFactor(
            key="confluence",
            title="Zone confluence" if positive else "Limited confluence",
            score=normalized,
            sentiment="POSITIVE" if positive else "NEGATIVE",
            summary=(
                f"{zone.merged_count} overlapping detections support this area."
                if positive
                else "No additional overlapping zone was confirmed."
            ),
            recommendation=(
                "Verify that the overlapping zones remain valid."
                if positive
                else "Higher-timeframe or structure confluence could improve quality."
            ),
            weight=15.0,
        )

    @staticmethod
    def _label(score: float) -> str:
        if score >= 90:
            return "Elite"
        if score >= 75:
            return "Strong"
        if score >= 60:
            return "Moderate"
        if score >= 40:
            return "Weak"
        return "Rejected"
