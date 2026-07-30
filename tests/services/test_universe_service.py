from pathlib import Path

import pytest

from backend.services.scanner.universe_service import UniverseService

DATA_DIRECTORY = Path(__file__).resolve().parents[2] / "backend" / "data" / "universes"


@pytest.mark.parametrize(
    ("universe", "expected_count"),
    [
        ("nifty50", 50),
        ("nifty100", 100),
        ("nifty200", 200),
        ("nse500", 500),
        ("fno", 208),
        ("allnse", 2390),
    ],
)
def test_predefined_universe_counts(universe: str, expected_count: int) -> None:
    symbols = UniverseService(DATA_DIRECTORY).get_symbols(universe)

    assert len(symbols) == expected_count
    assert len(symbols) == len(set(symbols))


def test_default_universe_is_nse500() -> None:
    assert len(UniverseService(DATA_DIRECTORY).get_symbols()) == 500


@pytest.mark.parametrize("universe", ["watchlist", "custom"])
def test_user_universe_uses_only_supplied_symbols(universe: str) -> None:
    symbols = UniverseService(DATA_DIRECTORY).get_symbols(
        universe,
        [" tcs ", "INFY", "TCS"],
    )

    assert symbols == ["INFY", "TCS"]
