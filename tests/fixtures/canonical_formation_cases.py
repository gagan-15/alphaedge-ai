"""Deterministic comparison cases for canonical zone formation."""

from __future__ import annotations

import pandas as pd


def _frame(rows: list[tuple[float, float, float, float]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=["Open", "High", "Low", "Close"])


FORMATION_CASES = {
    "dbr_strong": _frame(
        [
            (101, 102, 92, 93),
            (93, 94, 91, 92),
            (92, 106, 91, 105),
            (105, 114, 104, 113),
            (113, 117, 112, 116),
        ]
    ),
    "rbr_strong": _frame(
        [
            (82, 91, 81, 90),
            (90, 92, 89, 90.5),
            (90.5, 105, 90, 104),
            (104, 114, 103, 113),
            (113, 117, 112, 116),
        ]
    ),
    "rbd_strong": _frame(
        [
            (92, 101, 91, 100),
            (100, 101, 98, 99.5),
            (99.5, 100, 85, 86),
            (86, 87, 76, 77),
            (77, 78, 72, 73),
        ]
    ),
    "dbd_strong": _frame(
        [
            (101, 102, 92, 93),
            (93, 95, 92, 93.5),
            (93.5, 94, 79, 80),
            (80, 81, 70, 71),
            (71, 72, 66, 67),
        ]
    ),
    "boundary_50_percent": _frame(
        [
            (101, 102, 92, 93),
            (92, 98, 90, 96),
            (96, 108, 95, 107),
            (107, 116, 106, 115),
            (115, 119, 114, 118),
        ]
    ),
    "weak_single_departure": _frame(
        [
            (101, 102, 95, 96),
            (96, 97, 94, 95.5),
            (95.5, 105, 95, 104),
            (104, 105, 102, 103.5),
            (103.5, 104, 102, 103),
        ]
    ),
    "four_base_very_strong_gap": _frame(
        [
            (90, 94, 90, 93),
            (93, 94, 90, 90),
            (90, 94, 90, 93),
            (93, 94, 90, 90),
            (90, 94, 90, 93),
            (93, 94, 90, 90),
            (90, 94, 90, 93),
            (93, 94, 90, 90),
            (90, 94, 90, 93),
            (93, 94, 90, 90),
            (90, 94, 90, 93),
            (93, 94, 90, 90),
            (90, 94, 90, 93),
            (101, 102, 94, 95),
            (95, 96, 93, 94.5),
            (94.5, 95.5, 93.5, 94),
            (94, 95, 93, 94.4),
            (94.4, 95, 93.5, 94.2),
            (99, 112, 99, 111),
            (111, 124, 110, 123),
            (123, 127, 122, 126),
        ]
    ),
}

# Frozen output identifiers captured from the pre-Milestone 1.2/1.3 detector.
LEGACY_ACCEPTED = {
    ("dbr_strong", "DROP_BASE_RALLY", 1),
    ("rbr_strong", "RALLY_BASE_RALLY", 1),
    ("rbd_strong", "RALLY_BASE_DROP", 1),
    ("dbd_strong", "DROP_BASE_DROP", 1),
    ("boundary_50_percent", "DROP_BASE_RALLY", 1),
    ("weak_single_departure", "DROP_BASE_RALLY", 1),
}

CANONICAL_ACCEPTED = {
    ("dbr_strong", "DROP_BASE_RALLY", 1),
    ("rbr_strong", "RALLY_BASE_RALLY", 1),
    ("rbd_strong", "RALLY_BASE_DROP", 1),
    ("dbd_strong", "DROP_BASE_DROP", 1),
    ("weak_single_departure", "DROP_BASE_RALLY", 1),
    ("four_base_very_strong_gap", "DROP_BASE_RALLY", 4),
}
