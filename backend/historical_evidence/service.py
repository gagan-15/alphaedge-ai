# flake8: noqa: E501
"""Validation and aggregation service for immutable Historical Evidence."""

from __future__ import annotations

from math import ceil
from typing import Any

from backend.historical_evidence.constants import (
    DEFAULT_DATABASE_PATH,
    HISTORICAL_EVIDENCE_VERSION,
    INTERACTION_STATUSES,
    PATTERNS,
    SUPPORTED_TIMEFRAMES,
    TC_LABELS,
    ZONE_TYPES,
    ZQ_LABELS,
)
from backend.historical_evidence.repository import (
    HistoricalEvidenceFilters,
    HistoricalEvidenceRepository,
)


class HistoricalEvidenceValidationError(ValueError):
    """A public query cannot be evaluated against the frozen dataset."""


class HistoricalEvidenceVersionMismatch(HistoricalEvidenceValidationError):
    """The requested evidence version differs from the mounted artifact."""


class HistoricalEvidenceService:
    def __init__(self, repository: HistoricalEvidenceRepository | None = None) -> None:
        self.repository = repository or HistoricalEvidenceRepository(
            DEFAULT_DATABASE_PATH
        )

    def _verify_version(self, version: str) -> dict[str, Any]:
        metadata = self.repository.metadata()
        mounted = metadata.get("historical_evidence_version")
        if version != HISTORICAL_EVIDENCE_VERSION or mounted != version:
            raise HistoricalEvidenceVersionMismatch(
                f"Requested dataset version '{version}' is not available; mounted version is '{mounted}'."
            )
        return metadata

    @staticmethod
    def filters(
        *,
        timeframe: str | None = None,
        zone_type: str | None = None,
        pattern: str | None = None,
        zone_quality_label: str | None = None,
        trade_confidence_label: str | None = None,
        year: int | None = None,
        symbol: str | None = None,
        interaction_status: str = "ALL",
    ) -> HistoricalEvidenceFilters:
        normalized_timeframe = timeframe.upper() if timeframe else None
        aliases = {"DAILY": "1D", "WEEKLY": "1W"}
        normalized_timeframe = aliases.get(normalized_timeframe, normalized_timeframe)
        values = {
            "timeframe": (normalized_timeframe, SUPPORTED_TIMEFRAMES),
            "zone_type": (zone_type.upper() if zone_type else None, ZONE_TYPES),
            "pattern": (pattern.upper() if pattern else None, PATTERNS),
            "zone_quality_label": (
                zone_quality_label.upper() if zone_quality_label else None,
                ZQ_LABELS,
            ),
            "trade_confidence_label": (
                trade_confidence_label.upper() if trade_confidence_label else None,
                TC_LABELS,
            ),
            "interaction_status": (interaction_status.upper(), INTERACTION_STATUSES),
        }
        for name, (value, allowed) in values.items():
            if value is not None and value not in allowed:
                if name == "timeframe":
                    raise HistoricalEvidenceValidationError(
                        "Large-scale historical evidence is currently available only for Daily and Weekly zones."
                    )
                raise HistoricalEvidenceValidationError(f"Unsupported {name}: {value}")
        if year is not None and not 2021 <= year <= 2026:
            raise HistoricalEvidenceValidationError(
                "Year must be between 2021 and 2026."
            )
        return HistoricalEvidenceFilters(
            timeframe=values["timeframe"][0],
            zone_type=values["zone_type"][0],
            pattern=values["pattern"][0],
            zone_quality_label=values["zone_quality_label"][0],
            trade_confidence_label=values["trade_confidence_label"][0],
            year=year,
            symbol=symbol.strip().upper() if symbol else None,
            interaction_status=values["interaction_status"][0],
        )

    def metadata(self, version: str) -> dict[str, Any]:
        return self._verify_version(version)

    def summary(
        self, version: str, filters: HistoricalEvidenceFilters
    ) -> dict[str, Any]:
        metadata = self._verify_version(version)
        counts = self.repository.summary(filters)
        interacted = counts["interacted_zones"]
        available = counts["target_available"]

        def metric(numerator: int, denominator: int) -> dict[str, int | float | None]:
            return {
                "numerator": numerator,
                "denominator": denominator,
                "percent": (
                    round(numerator * 100 / denominator, 2) if denominator else None
                ),
            }

        reliability = (
            "INSUFFICIENT"
            if interacted < 30
            else (
                "EXPLORATORY"
                if interacted < 100
                else "MODERATE_EVIDENCE" if interacted < 300 else "STRONGER_EVIDENCE"
            )
        )
        return {
            "historical_evidence_version": metadata["historical_evidence_version"],
            "methodology_fingerprint": metadata["methodology_fingerprint"],
            "filters": (
                filters.__dict__
                if hasattr(filters, "__dict__")
                else {field: getattr(filters, field) for field in filters.__slots__}
            ),
            "historical_zones": counts["historical_zones"],
            "interacted_zones": interacted,
            "interaction_rate": metric(interacted, counts["historical_zones"]),
            "reaction_1_zone_width": metric(counts["reaction_1"], interacted),
            "reaction_2_zone_width": metric(counts["reaction_2"], interacted),
            "reaction_3_zone_width": metric(counts["reaction_3"], interacted),
            "reaction_5_zone_width": metric(counts["reaction_5"], interacted),
            "structural_survival": metric(counts["survived"], interacted),
            "structural_target_availability": metric(available, interacted),
            "structural_target_achievement": metric(
                counts["target_achieved"], available
            ),
            "median_mfe_zone_width": counts["median_mfe_zone_width"],
            "median_mae_zone_width": counts["median_mae_zone_width"],
            "reliability": reliability,
            "empty_cohort": counts["historical_zones"] == 0,
        }

    def zones(
        self, version: str, filters: HistoricalEvidenceFilters, **pagination: Any
    ) -> dict[str, Any]:
        metadata = self._verify_version(version)
        total, items = self.repository.zones(filters, **pagination)
        page = pagination["page"]
        page_size = pagination["page_size"]
        return {
            "historical_evidence_version": metadata["historical_evidence_version"],
            "methodology_fingerprint": metadata["methodology_fingerprint"],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": ceil(total / page_size) if total else 0,
            "items": items,
        }

    def comparable_zone(
        self,
        version: str,
        *,
        zone_id: str,
        timeframe: str,
        zone_type: str,
        pattern: str,
        zone_quality_label: str,
        trade_confidence_label: str,
        current_methodology_version: str,
    ) -> dict[str, Any]:
        """Resolve the frozen comparable cohort without touching live engines."""
        from backend.config.canonical_methodology import (
            CANONICAL_FORMATION_VERSION,
            SCANNER_METHODOLOGY_CACHE_VERSION,
        )

        metadata = self._verify_version(version)
        frozen_formation = metadata.get("methodology", {}).get("formation")
        expected_formation = f"canonical-formation-{CANONICAL_FORMATION_VERSION}"
        if (
            current_methodology_version != SCANNER_METHODOLOGY_CACHE_VERSION
            or frozen_formation != expected_formation
        ):
            raise HistoricalEvidenceVersionMismatch(
                "Historical evidence is unavailable for the current methodology version."
            )

        inputs = {
            "zone_id": zone_id,
            "timeframe": timeframe,
            "zone_type": zone_type,
            "pattern": pattern,
            "zone_quality_label": zone_quality_label,
            "trade_confidence_label": trade_confidence_label,
            "current_methodology_version": current_methodology_version,
        }
        normalized_timeframe = timeframe.upper()
        aliases = {"DAILY": "1D", "WEEKLY": "1W"}
        normalized_timeframe = aliases.get(normalized_timeframe, normalized_timeframe)
        inputs["timeframe"] = normalized_timeframe

        base = {
            "historical_evidence_version": metadata["historical_evidence_version"],
            "methodology_fingerprint": metadata["methodology_fingerprint"],
            "current_zone": inputs,
        }
        if normalized_timeframe not in SUPPORTED_TIMEFRAMES:
            return base | {
                "status": "UNSUPPORTED_TIMEFRAME",
                "selected_match_level": None,
                "exact_level_1": None,
                "selected_cohort": None,
                "summary_metrics": None,
                "reliability": "INSUFFICIENT",
                "applied_cohort_definition": None,
                "explanation": "Large-scale comparable historical evidence is currently available for Daily and Weekly zones.",
            }

        common = {
            "timeframe": normalized_timeframe,
            "zone_type": zone_type,
            "trade_confidence_label": trade_confidence_label,
        }
        validated_common = self.filters(**common)

        if validated_common.trade_confidence_label == "VERY_HIGH":
            return base | {
                "status": "NO_COMPARABLE_HISTORICAL_EVIDENCE",
                "selected_match_level": None,
                "exact_level_1": {"historical_zones": 0, "interacted_zones": 0},
                "selected_cohort": None,
                "summary_metrics": None,
                "reliability": "INSUFFICIENT",
                "applied_cohort_definition": None,
                "explanation": "No historical VERY_HIGH observations are available in the frozen Milestone 9C dataset.",
            }

        level_filters = (
            self.filters(
                **common,
                pattern=pattern,
                zone_quality_label=zone_quality_label,
            ),
            self.filters(**common, zone_quality_label=zone_quality_label),
            validated_common,
        )
        summaries = tuple(self.summary(version, cohort) for cohort in level_filters)
        exact_level_1 = {
            "historical_zones": summaries[0]["historical_zones"],
            "interacted_zones": summaries[0]["interacted_zones"],
        }
        if summaries[2]["historical_zones"] == 0:
            return base | {
                "status": "NO_COMPARABLE_HISTORICAL_EVIDENCE",
                "selected_match_level": 3,
                "exact_level_1": exact_level_1,
                "selected_cohort": {
                    "historical_zones": 0,
                    "interacted_zones": 0,
                },
                "summary_metrics": summaries[2],
                "reliability": "INSUFFICIENT",
                "applied_cohort_definition": {
                    "timeframe": normalized_timeframe,
                    "zone_type": zone_type.upper(),
                    "trade_confidence_label": trade_confidence_label.upper(),
                },
                "explanation": "No comparable historical evidence exists for this timeframe, direction, and Trade Confidence label.",
            }

        selected_index = next(
            (
                index
                for index, summary in enumerate(summaries)
                if summary["interacted_zones"] >= 30
            ),
            2,
        )
        selected = summaries[selected_index]
        level = selected_index + 1
        definitions = (
            {
                "timeframe": normalized_timeframe,
                "zone_type": zone_type.upper(),
                "pattern": pattern.upper(),
                "zone_quality_label": zone_quality_label.upper(),
                "trade_confidence_label": trade_confidence_label.upper(),
            },
            {
                "timeframe": normalized_timeframe,
                "zone_type": zone_type.upper(),
                "zone_quality_label": zone_quality_label.upper(),
                "trade_confidence_label": trade_confidence_label.upper(),
            },
            {
                "timeframe": normalized_timeframe,
                "zone_type": zone_type.upper(),
                "trade_confidence_label": trade_confidence_label.upper(),
            },
        )
        explanations = (
            "Closest historical match using the same timeframe, direction, pattern, Zone Quality, and Trade Confidence.",
            "Pattern broadened because the closest historical cohort did not contain enough interacted observations.",
            "Zone Quality broadened because narrower historical cohorts were too small.",
        )
        return base | {
            "status": "AVAILABLE",
            "selected_match_level": level,
            "exact_level_1": exact_level_1,
            "selected_cohort": {
                "historical_zones": selected["historical_zones"],
                "interacted_zones": selected["interacted_zones"],
            },
            "summary_metrics": selected,
            "reliability": selected["reliability"],
            "applied_cohort_definition": definitions[selected_index],
            "explanation": explanations[selected_index],
        }
