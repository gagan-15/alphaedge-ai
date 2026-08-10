"""
Zone Detection Engine for AlphaEdge AI.

Sprint:
    2.26 - Zone Detection Engine
"""

from pandas import DataFrame

from backend.core.logger import logger
from backend.engines.demand_supply_engine.base_detector import (
    BaseDetector,
)
from backend.engines.demand_supply_engine.departure_detector import (
    DepartureDetector,
)
from backend.engines.demand_supply_engine.pattern_detector import (
    PatternDetector,
)
from backend.engines.demand_supply_engine.zone_boundary_engine import (
    ZoneBoundaryEngine,
)
from backend.engines.demand_supply_engine.candle_classifier import CandleClassifier
from backend.config.settings import MAX_BASE_CANDLES, MIN_BASE_CANDLES
from backend.models.departure import (
    Departure,
    DepartureDirection,
    DepartureStrength,
)
from backend.models.zone import (
    Zone,
    ZoneType,
)
from backend.validators.zone_validator import (
    ZoneValidator,
)
from backend.models.candle_classification import CandleStructure
from backend.models.formation_evidence import (
    CanonicalFormationEvidence,
    FormationCandleEvidence,
)
from backend.validators.zone_boundary_validator import BoundaryValidationError


class ZoneDetectionEngine:
    """
    Detect Demand and Supply zones.

    This class orchestrates the complete
    zone detection workflow.

    Responsibilities

    1. Detect Bases
    2. Detect Departures
    3. Detect Patterns
    4. Create Zones
    5. Validate Zones
    """

    def __init__(self) -> None:

        self._base_detector = BaseDetector()

        self._departure_detector = DepartureDetector()

        self._pattern_detector = PatternDetector()

        self._boundary_engine = ZoneBoundaryEngine()

        self._candle_classifier = CandleClassifier()

    def detect_zones(
        self,
        market_data: DataFrame,
    ) -> list[Zone]:
        """
        Detect all valid demand
        and supply zones.
        """

        logger.info("Starting zone detection.")

        detected_zones: list[Zone] = []

        base_regions = self._base_detector.detect(market_data)

        logger.info(f"{len(base_regions)} base region(s) detected.")

        for base in base_regions:

            departure = self._departure_detector.detect(
                market_data,
                base,
            )

            if departure is None:

                logger.info("Skipping base because " "no valid departure exists.")

                continue

            if (
                base.candle_count > MAX_BASE_CANDLES
                and departure.strength != DepartureStrength.VERY_STRONG
            ):
                logger.info(
                    "Skipping extended base because departure is not very strong."
                )
                continue

            leg_in_bullish = (
                departure.leg_in_direction == DepartureDirection.BULLISH
            )

            pattern = self._pattern_detector.detect(
                leg_in_bullish,
                departure,
            )

            try:
                zone = self._create_zone(
                    market_data,
                    base,
                    pattern,
                    departure,
                )
            except BoundaryValidationError as error:
                logger.info(
                    "Rejecting zone boundary: %s.",
                    error.reason_code.value,
                )
                continue

            ZoneValidator.validate_zone(zone)

            detected_zones.append(zone)

        logger.info(
            "Zone detection completed. " f"{len(detected_zones)} zone(s) detected."
        )

        return detected_zones

    def detect_zones_with_diagnostics(
        self,
        market_data: DataFrame,
    ) -> tuple[list[Zone], list[dict[str, object]]]:
        """Run the production detector and expose its candidate lifecycle."""

        accepted = self.detect_zones(market_data)
        accepted_by_index = {zone.created_index: zone for zone in accepted}
        bases = self._base_detector.detect(market_data)
        base_checks = self._base_detector.diagnose(market_data)
        diagnostics: list[dict[str, object]] = []

        # Candles rejected before a base could be formed.
        for check in base_checks:
            if check["passed"]:
                continue
            index = int(check["index"])
            candle = market_data.iloc[index]
            diagnostics.append(
                {
                    "candidate_id": f"NF-{index + 1}",
                    "pattern": None,
                    "base_start_index": index,
                    "base_end_index": index,
                    "proximal": float(candle["High"]),
                    "distal": float(candle["Low"]),
                    "zone_type": None,
                    "status": "rejected",
                    "score": None,
                    "rejection_reasons": [
                        "Candidate not formed: candle body is larger than "
                        "the production base limit."
                    ],
                    "rule_results": [
                        {
                            "key": "valid_base",
                            "label": "Valid base candle",
                            "passed": False,
                            "actual": round(float(check["body_percent"]), 2),
                            "required": f"At most {check['maximum_body_percent']}%",
                        }
                    ],
                }
            )

        for base in bases:
            base_data = market_data.iloc[base.start_index : base.end_index + 1]
            departure, departure_rules = self._departure_detector.diagnose(
                market_data, base
            )
            zone = accepted_by_index.get(base.end_index)
            rules = [
                {
                    "key": "base_candle_count",
                    "label": "Base candle count",
                    "passed": True,
                    "actual": base.candle_count,
                    "required": (
                        f"{MIN_BASE_CANDLES}-{MAX_BASE_CANDLES}, or up to 5 "
                        "with Very Strong departure"
                    ),
                },
                *departure_rules,
            ]
            failed = [str(rule["label"]) for rule in rules if not rule["passed"]]
            if departure is None or zone is None:
                direction = None
                attempted_pattern = None
                if departure is not None:
                    direction = (
                        "DEMAND"
                        if departure.direction == DepartureDirection.BULLISH
                        else "SUPPLY"
                    )
                    attempted_pattern = self._pattern_detector.detect(
                        departure.leg_in_direction == DepartureDirection.BULLISH,
                        departure,
                    ).pattern_type.value
                elif base.end_index + 1 < len(market_data):
                    next_close = float(market_data.iloc[base.end_index + 1]["Close"])
                    base_high = float(base_data["High"].max())
                    base_low = float(base_data["Low"].min())
                    attempted_direction = (
                        DepartureDirection.BULLISH
                        if next_close > base_high
                        else (
                            DepartureDirection.BEARISH
                            if next_close < base_low
                            else None
                        )
                    )
                    if attempted_direction is not None:
                        direction = (
                            "DEMAND"
                            if attempted_direction == DepartureDirection.BULLISH
                            else "SUPPLY"
                        )
                        attempted_pattern = self._pattern_detector.detect(
                            self._is_leg_in_bullish(market_data, base.start_index),
                            Departure(
                                direction=attempted_direction,
                                departure_index=base.end_index + 1,
                            ),
                        ).pattern_type.value
                diagnostics.append(
                    {
                        "candidate_id": f"C-{base.start_index + 1}",
                        "pattern": attempted_pattern,
                        "base_start_index": base.start_index,
                        "base_end_index": base.end_index,
                        "proximal": float(base_data["High"].max()),
                        "distal": float(base_data["Low"].min()),
                        "zone_type": direction,
                        "status": "rejected",
                        "score": None,
                        "rejection_reasons": failed or ["Candidate not formed"],
                        "rule_results": rules,
                    }
                )
                continue
            diagnostics.append(
                {
                    "candidate_id": f"C-{base.start_index + 1}",
                    "pattern": zone.pattern_type,
                    "base_start_index": base.start_index,
                    "base_end_index": base.end_index,
                    "proximal": (
                        zone.upper_price
                        if zone.zone_type == ZoneType.DEMAND
                        else zone.lower_price
                    ),
                    "distal": (
                        zone.lower_price
                        if zone.zone_type == ZoneType.DEMAND
                        else zone.upper_price
                    ),
                    "zone_type": zone.zone_type.value,
                    "status": "accepted",
                    "score": None,
                    "rejection_reasons": [],
                    "rule_results": rules,
                }
            )
        return accepted, diagnostics

    def _create_zone(
        self,
        market_data: DataFrame,
        base,
        pattern,
        departure: Departure,
    ) -> Zone:
        """
        Create a Zone object from
        a detected BaseRegion.
        """

        boundary_result = self._boundary_engine.calculate(
            market_data=market_data,
            base=base,
            pattern_type=pattern.pattern_type,
            departure=departure,
        )
        zone_type = self._boundary_engine.zone_type_for(pattern.pattern_type)
        if zone_type == ZoneType.DEMAND:
            upper_price = boundary_result.selected.proximal
            lower_price = boundary_result.selected.distal
        else:
            upper_price = boundary_result.selected.distal
            lower_price = boundary_result.selected.proximal

        logger.info(
            "Creating %s zone.",
            zone_type.value,
        )

        return Zone(
            zone_type=zone_type,
            upper_price=upper_price,
            lower_price=lower_price,
            created_index=base.end_index,
            pattern_type=pattern.pattern_type.value,
            boundary_result=boundary_result,
            formation_evidence=self._build_formation_evidence(
                market_data, base, pattern, departure
            ),
        )

    def _build_formation_evidence(
        self, market_data: DataFrame, base, pattern, departure: Departure
    ) -> CanonicalFormationEvidence:
        """Freeze evidence established during canonical formation."""
        if any(
            value is None
            for value in (
                departure.leg_in_start_index,
                departure.leg_in_end_index,
                departure.end_index,
                departure.leg_in_direction,
                departure.strength,
                departure.closing_comparison_reference,
                departure.qualifying_close,
                departure.acceptance_reason,
            )
        ):
            raise ValueError("Accepted departure is missing canonical evidence.")

        leg_in = self._candle_evidence(
            market_data, departure.leg_in_start_index, departure.leg_in_end_index
        )
        base_candles = self._candle_evidence(
            market_data, base.start_index, base.end_index
        )
        leg_out = self._candle_evidence(
            market_data, departure.departure_index, departure.end_index
        )
        second = leg_out[1] if len(leg_out) > 1 else None
        names = {
            "DROP_BASE_RALLY": "DBR",
            "RALLY_BASE_RALLY": "RBR",
            "RALLY_BASE_DROP": "RBD",
            "DROP_BASE_DROP": "DBD",
        }
        return CanonicalFormationEvidence(
            pattern=names[pattern.pattern_type.value],
            leg_in_start_index=departure.leg_in_start_index,
            leg_in_end_index=departure.leg_in_end_index,
            leg_in_timestamps=tuple(item.timestamp for item in leg_in),
            leg_in_candles=leg_in,
            leg_in_direction=departure.leg_in_direction,
            base_start_index=base.start_index,
            base_end_index=base.end_index,
            base_timestamps=tuple(item.timestamp for item in base_candles),
            base_candles=base_candles,
            base_body_ratios=tuple(
                item.classification.body_ratio for item in base_candles
            ),
            base_candle_count=base.candle_count,
            leg_out_start_index=departure.departure_index,
            leg_out_end_index=departure.end_index,
            leg_out_timestamps=tuple(item.timestamp for item in leg_out),
            leg_out_candles=leg_out,
            first_leg_out_exciting=(
                leg_out[0].classification.structure == CandleStructure.EXCITING
            ),
            first_leg_out_explosive=leg_out[0].classification.explosive,
            second_leg_out_exciting=(
                None
                if second is None
                else second.classification.structure == CandleStructure.EXCITING
            ),
            second_leg_out_explosive=(
                None if second is None else second.classification.explosive
            ),
            significant_gap=departure.significant_gap,
            gap_measurement=departure.gap_measurement,
            departure_strength=departure.strength,
            closing_rule_passed=departure.good_closing,
            closing_comparison_reference=departure.closing_comparison_reference,
            qualifying_close=departure.qualifying_close,
            acceptance_reason=departure.acceptance_reason,
        )

    def _candle_evidence(
        self, market_data: DataFrame, start_index: int, end_index: int
    ) -> tuple[FormationCandleEvidence, ...]:
        evidence = []
        for index in range(start_index, end_index + 1):
            timestamp = market_data.index[index]
            isoformat = getattr(timestamp, "isoformat", None)
            evidence.append(
                FormationCandleEvidence(
                    index=index,
                    timestamp=isoformat() if callable(isoformat) else str(timestamp),
                    classification=self._candle_classifier.classify(
                        market_data, index
                    ),
                )
            )
        return tuple(evidence)

    @staticmethod
    def _is_leg_in_bullish(
        market_data: DataFrame,
        base_start_index: int,
    ) -> bool:
        """
        Determine the direction of the
        candle immediately before the base.

        Returns:
            True:
                Bullish leg-in.

            False:
                Bearish leg-in.
        """

        if base_start_index == 0:
            return False

        previous_candle = market_data.iloc[base_start_index - 1]

        return float(previous_candle["Close"]) > float(previous_candle["Open"])
