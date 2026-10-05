"""Tests for the scanner's non-scoring reaction status extension."""

import pandas as pd
import pytest

from backend.api.scanner import _reaction_state
from backend.config.scanner_config import ScannerConfig
from backend.models.zone import Zone, ZoneType


def _candles(rows: list[tuple[float, float, float]]) -> pd.DataFrame:
    index = pd.date_range("2026-01-01", periods=len(rows), freq="D")
    return pd.DataFrame(
        {
            "High": [row[0] for row in rows],
            "Low": [row[1] for row in rows],
            "Close": [row[2] for row in rows],
        },
        index=index,
    )


def test_demand_zone_is_reacting_after_crossing_above_proximal() -> None:
    zone = Zone(ZoneType.DEMAND, upper_price=100, lower_price=95, created_index=0)
    data = _candles(
        [
            (100, 95, 98),
            (104, 100, 103),
            (108, 103, 107),
            (110, 105, 108),
            (101, 96, 98),
            (103, 98, 101),
            (104, 101, 103),
        ]
    )

    reaction = _reaction_state(zone, data, 5)

    assert reaction["active"] is True
    assert reaction["percent"] == 3.0
    assert reaction["duration"] == 2


def test_supply_zone_is_reacting_after_crossing_below_proximal() -> None:
    zone = Zone(ZoneType.SUPPLY, upper_price=155, lower_price=150, created_index=0)
    data = _candles(
        [
            (155, 150, 152),
            (150, 146, 147),
            (147, 142, 144),
            (145, 140, 142),
            (154, 149, 152),
            (152, 147, 148),
        ]
    )

    reaction = _reaction_state(zone, data, 5)

    assert reaction["active"] is True
    assert reaction["percent"] == 1.33


def test_reaction_ends_after_configured_threshold() -> None:
    zone = Zone(ZoneType.DEMAND, upper_price=100, lower_price=95, created_index=0)
    data = _candles(
        [
            (100, 95, 98),
            (104, 100, 103),
            (108, 103, 107),
            (110, 105, 108),
            (101, 96, 98),
            (103, 98, 101),
            (107, 101, 106),
        ]
    )

    reaction = _reaction_state(zone, data, 5)

    assert reaction["active"] is False
    assert reaction["percent"] == 6.0
    assert reaction["ended"] is not None


def test_reaction_threshold_accepts_only_supported_values() -> None:
    assert ScannerConfig(reaction_completion_percent=7).reaction_completion_percent == 7
    with pytest.raises(ValueError):
        ScannerConfig(reaction_completion_percent=4)
