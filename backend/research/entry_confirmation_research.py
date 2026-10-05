"""Point-in-time Entry Confirmation feature study for Milestone 11A.

Research only. Production code does not import this module. Candidate flags are
descriptive tests, not an activated Entry Confirmation methodology.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import median
from typing import Any

from pandas import DataFrame

from backend.engines.demand_supply_engine.zone_detection_engine import (
    ZoneDetectionEngine,
)
from backend.models.zone import Zone, ZoneType


@dataclass(frozen=True)
class ConfirmationObservation:
    symbol: str
    timeframe: str
    zone_id: str
    zone_type: str
    pattern: str
    interaction_index: int
    interaction_timestamp: str
    penetration_percent: float
    same_candle_ambiguous: bool
    wick_rejection_index: int | None
    close_recovery_index: int | None
    engulfing_response_index: int | None
    displacement_index: int | None
    failed_continuation_index: int | None
    micro_structure_index: int | None
    volume_expansion_index: int | None
    gap_response_index: int | None
    reaction_detected_index: int | None
    structural_confirmation_index: int | None
    structural_failure_index: int | None
    mfe_zone_width_from_interaction: float
    mae_zone_width_from_interaction: float
    close_recovery_post_mfe_zw: float | None
    reaction_detected_post_mfe_zw: float | None
    structural_confirmation_post_mfe_zw: float | None
    close_recovery_pre_move_zw: float | None
    reaction_detected_pre_move_zw: float | None
    structural_confirmation_pre_move_zw: float | None


class EntryConfirmationResearchEngine:
    """Observe post-formation interaction using only candles known at each event."""

    def __init__(self) -> None:
        self._zones = ZoneDetectionEngine()

    def replay(
        self, data: DataFrame, *, symbol: str, timeframe: str
    ) -> list[dict[str, Any]]:
        observations: list[dict[str, Any]] = []
        for zone in self._zones.detect_zones(data):
            observation = self._observe(data, zone, symbol=symbol, timeframe=timeframe)
            if observation is not None:
                observations.append(asdict(observation))
        return observations

    def _observe(
        self, data: DataFrame, zone: Zone, *, symbol: str, timeframe: str
    ) -> ConfirmationObservation | None:
        evidence = zone.formation_evidence
        if evidence is None:
            return None
        start = evidence.leg_out_end_index + 1
        interaction = self._first_interaction(data, zone, start)
        if interaction is None:
            return None
        low, high = sorted((float(zone.lower_price), float(zone.upper_price)))
        width = max(high - low, 1e-12)
        demand = zone.zone_type == ZoneType.DEMAND
        row = data.iloc[interaction]
        penetration = self._penetration(row, low, high, demand)
        end = min(len(data), interaction + 21)
        failure = self._failure_index(data, low, high, demand, interaction, end)
        horizon_end = min(failure + 1 if failure is not None else end, len(data))
        future = data.iloc[interaction:horizon_end]
        if future.empty:
            return None
        reference = high if demand else low
        if demand:
            mfe = (float(future["High"].max()) - reference) / width
            mae = (reference - float(future["Low"].min())) / width
        else:
            mfe = (reference - float(future["Low"].min())) / width
            mae = (float(future["High"].max()) - reference) / width
        candidates = {
            "wick_rejection_index": self._first_matching(
                data,
                interaction,
                horizon_end,
                lambda i: self._wick_rejection(data.iloc[i], demand),
            ),
            "close_recovery_index": self._first_matching(
                data,
                interaction,
                horizon_end,
                lambda i: self._close_recovery(data.iloc[i], reference, demand),
            ),
            "engulfing_response_index": self._first_matching(
                data,
                interaction + 1,
                horizon_end,
                lambda i: self._engulfing(data.iloc[i - 1], data.iloc[i], demand),
            ),
            "displacement_index": self._first_matching(
                data,
                interaction,
                horizon_end,
                lambda i: self._displaced(data.iloc[i], reference, width, demand),
            ),
            "failed_continuation_index": self._first_matching(
                data,
                interaction + 1,
                horizon_end,
                lambda i: self._failed_continuation(
                    data.iloc[i - 1], data.iloc[i], demand
                ),
            ),
            "micro_structure_index": self._micro_structure(
                data, interaction, horizon_end, demand
            ),
            "volume_expansion_index": self._volume_expansion(
                data, interaction, horizon_end
            ),
            "gap_response_index": self._gap_response(
                data, interaction, horizon_end, demand
            ),
        }
        independent = (
            candidates["wick_rejection_index"],
            candidates["engulfing_response_index"],
            candidates["failed_continuation_index"],
            candidates["volume_expansion_index"],
            candidates["gap_response_index"],
        )
        close_index = candidates["close_recovery_index"]
        reaction_index = (
            max(close_index, min(value for value in independent if value is not None))
            if close_index is not None
            and any(value is not None for value in independent)
            else None
        )
        micro_index = candidates["micro_structure_index"]
        displacement_index = candidates["displacement_index"]
        structural_index = (
            max(micro_index, displacement_index)
            if micro_index is not None and displacement_index is not None
            else None
        )

        def tier_outcome(index: int | None) -> tuple[float | None, float | None]:
            if index is None or index >= horizon_end:
                return None, None
            before = data.iloc[interaction : index + 1]
            after = data.iloc[index:horizon_end]
            if demand:
                pre_move = (float(before["High"].max()) - reference) / width
                post_move = (
                    float(after["High"].max()) - float(data.iloc[index]["Close"])
                ) / width
            else:
                pre_move = (reference - float(before["Low"].min())) / width
                post_move = (
                    float(data.iloc[index]["Close"]) - float(after["Low"].min())
                ) / width
            return round(max(0.0, post_move), 4), round(max(0.0, pre_move), 4)

        close_post, close_pre = tier_outcome(close_index)
        reaction_post, reaction_pre = tier_outcome(reaction_index)
        structural_post, structural_pre = tier_outcome(structural_index)
        return ConfirmationObservation(
            symbol=symbol,
            timeframe=timeframe,
            zone_id=str(
                getattr(zone, "zone_id", f"{symbol}-{timeframe}-{zone.created_index}")
            ),
            zone_type=zone.zone_type.value,
            pattern=str(evidence.pattern),
            interaction_index=interaction,
            interaction_timestamp=str(data.index[interaction]),
            penetration_percent=round(penetration, 4),
            same_candle_ambiguous=any(
                value == interaction for value in candidates.values()
            ),
            structural_failure_index=failure,
            mfe_zone_width_from_interaction=round(max(0.0, mfe), 4),
            mae_zone_width_from_interaction=round(max(0.0, mae), 4),
            reaction_detected_index=reaction_index,
            structural_confirmation_index=structural_index,
            close_recovery_post_mfe_zw=close_post,
            reaction_detected_post_mfe_zw=reaction_post,
            structural_confirmation_post_mfe_zw=structural_post,
            close_recovery_pre_move_zw=close_pre,
            reaction_detected_pre_move_zw=reaction_pre,
            structural_confirmation_pre_move_zw=structural_pre,
            **candidates,
        )

    @staticmethod
    def _first_interaction(data: DataFrame, zone: Zone, start: int) -> int | None:
        low, high = sorted((float(zone.lower_price), float(zone.upper_price)))
        for index in range(start, len(data)):
            row = data.iloc[index]
            if float(row["Low"]) <= high and float(row["High"]) >= low:
                return index
        return None

    @staticmethod
    def _penetration(row: Any, low: float, high: float, demand: bool) -> float:
        width = max(high - low, 1e-12)
        value = (
            (high - float(row["Low"])) / width
            if demand
            else (float(row["High"]) - low) / width
        )
        return max(0.0, min(100.0, 100.0 * value))

    @staticmethod
    def _failure_index(
        data: DataFrame, low: float, high: float, demand: bool, start: int, end: int
    ) -> int | None:
        for index in range(start, end):
            row = data.iloc[index]
            if (demand and float(row["Low"]) < low) or (
                not demand and float(row["High"]) > high
            ):
                return index
        return None

    @staticmethod
    def _first_matching(
        data: DataFrame, start: int, end: int, predicate: Any
    ) -> int | None:
        for index in range(max(0, start), end):
            if predicate(index):
                return index
        return None

    @staticmethod
    def _wick_rejection(row: Any, demand: bool) -> bool:
        open_, close, high, low = map(
            float, (row["Open"], row["Close"], row["High"], row["Low"])
        )
        body = abs(close - open_)
        wick = min(open_, close) - low if demand else high - max(open_, close)
        close_position = (close - low) / max(high - low, 1e-12)
        return wick > body and (
            close_position >= 0.5 if demand else close_position <= 0.5
        )

    @staticmethod
    def _close_recovery(row: Any, proximal: float, demand: bool) -> bool:
        close = float(row["Close"])
        return close > proximal if demand else close < proximal

    @staticmethod
    def _engulfing(previous: Any, current: Any, demand: bool) -> bool:
        po, pc = float(previous["Open"]), float(previous["Close"])
        co, cc = float(current["Open"]), float(current["Close"])
        direction = cc > co if demand else cc < co
        return direction and min(co, cc) <= min(po, pc) and max(co, cc) >= max(po, pc)

    @staticmethod
    def _displaced(row: Any, proximal: float, width: float, demand: bool) -> bool:
        close = float(row["Close"])
        return close >= proximal + width if demand else close <= proximal - width

    @staticmethod
    def _failed_continuation(previous: Any, current: Any, demand: bool) -> bool:
        if demand:
            return float(current["Low"]) >= float(previous["Low"]) and float(
                current["Close"]
            ) > float(previous["Close"])
        return float(current["High"]) <= float(previous["High"]) and float(
            current["Close"]
        ) < float(previous["Close"])

    @staticmethod
    def _micro_structure(
        data: DataFrame, interaction: int, end: int, demand: bool
    ) -> int | None:
        lookback = data.iloc[max(0, interaction - 3) : interaction]
        if lookback.empty:
            return None
        level = float(lookback["High"].max() if demand else lookback["Low"].min())
        for index in range(interaction, end):
            close = float(data.iloc[index]["Close"])
            if (demand and close > level) or (not demand and close < level):
                return index
        return None

    @staticmethod
    def _volume_expansion(data: DataFrame, interaction: int, end: int) -> int | None:
        if "Volume" not in data or interaction < 20:
            return None
        for index in range(interaction, end):
            average = float(data.iloc[index - 20 : index]["Volume"].mean())
            if average > 0 and float(data.iloc[index]["Volume"]) >= 1.5 * average:
                return index
        return None

    @staticmethod
    def _gap_response(
        data: DataFrame, interaction: int, end: int, demand: bool
    ) -> int | None:
        for index in range(max(1, interaction), end):
            previous = data.iloc[index - 1]
            current = data.iloc[index]
            if (demand and float(current["Low"]) > float(previous["High"])) or (
                not demand and float(current["High"]) < float(previous["Low"])
            ):
                return index
        return None


def summarize_confirmation_observations(
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compare each descriptive feature with the all-interaction baseline."""

    features = (
        "wick_rejection",
        "close_recovery",
        "engulfing_response",
        "displacement",
        "failed_continuation",
        "micro_structure",
        "volume_expansion",
        "gap_response",
    )

    def summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
        count = len(rows)
        return {
            "observations": count,
            "at_least_1zw": sum(
                row["mfe_zone_width_from_interaction"] >= 1 for row in rows
            ),
            "at_least_2zw": sum(
                row["mfe_zone_width_from_interaction"] >= 2 for row in rows
            ),
            "structural_survival": sum(
                row["structural_failure_index"] is None for row in rows
            ),
            "median_mfe_zw": (
                round(median(row["mfe_zone_width_from_interaction"] for row in rows), 4)
                if rows
                else None
            ),
        }

    output = {"baseline": summary(records), "features": {}, "tiers": {}}
    for feature in features:
        key = f"{feature}_index"
        rows = [row for row in records if row[key] is not None]
        result = summary(rows)
        result["coverage_percent"] = (
            round(100 * len(rows) / len(records), 2) if records else None
        )
        delays = [row[key] - row["interaction_index"] for row in rows]
        result["median_delay_candles"] = round(median(delays), 2) if delays else None
        result["same_candle_ambiguous"] = sum(
            row[key] == row["interaction_index"] for row in rows
        )
        output["features"][feature] = result
    tiers = {
        "tier_1_close_recovery": "close_recovery",
        "tier_2_reaction_detected": "reaction_detected",
        "tier_3_structural_confirmation": "structural_confirmation",
    }
    for tier, prefix in tiers.items():
        index_key = f"{prefix}_index"
        post_key = f"{prefix}_post_mfe_zw"
        pre_key = f"{prefix}_pre_move_zw"
        rows = [row for row in records if row.get(index_key) is not None]
        post_values = [row[post_key] for row in rows if row.get(post_key) is not None]
        pre_values = [row[pre_key] for row in rows if row.get(pre_key) is not None]
        delays = [row[index_key] - row["interaction_index"] for row in rows]
        sorted_delays = sorted(delays)

        def percentile(values: list[int], fraction: float) -> float | None:
            if not values:
                return None
            return float(values[round((len(values) - 1) * fraction)])

        output["tiers"][tier] = {
            "observations": len(rows),
            "coverage_percent": (
                round(100 * len(rows) / len(records), 2) if records else None
            ),
            "post_confirmation_at_least_1zw": sum(value >= 1 for value in post_values),
            "post_confirmation_at_least_2zw": sum(value >= 2 for value in post_values),
            "post_confirmation_at_least_3zw": sum(value >= 3 for value in post_values),
            "post_confirmation_2zw_percent": (
                round(
                    100 * sum(value >= 2 for value in post_values) / len(post_values), 2
                )
                if post_values
                else None
            ),
            "median_post_confirmation_mfe_zw": (
                round(median(post_values), 4) if post_values else None
            ),
            "median_pre_confirmation_move_zw": (
                round(median(pre_values), 4) if pre_values else None
            ),
            "median_delay_candles": round(median(delays), 2) if delays else None,
            "p75_delay_candles": percentile(sorted_delays, 0.75),
            "p90_delay_candles": percentile(sorted_delays, 0.90),
            "subsequent_failure": sum(
                row["structural_failure_index"] is not None
                and row["structural_failure_index"] >= row[index_key]
                for row in rows
            ),
            "same_candle_ambiguous": sum(
                row[index_key] == row["interaction_index"] for row in rows
            ),
        }
    return output
