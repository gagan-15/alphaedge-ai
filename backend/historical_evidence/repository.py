# flake8: noqa: E501
"""Read-only SQLite repository for frozen Milestone 9C evidence."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class HistoricalEvidenceFilters:
    timeframe: str | None = None
    zone_type: str | None = None
    pattern: str | None = None
    zone_quality_label: str | None = None
    trade_confidence_label: str | None = None
    year: int | None = None
    symbol: str | None = None
    interaction_status: str = "ALL"


class HistoricalEvidenceRepository:
    """Query an immutable SQLite artifact without write capability."""

    SORT_COLUMNS = {
        "formation_timestamp": "planning_timestamp",
        "symbol": "symbol",
        "timeframe": "timeframe",
        "zone_type": "zone_type",
        "pattern": "pattern",
        "zone_quality": "zone_quality_score",
        "trade_confidence": "trade_confidence_score",
        "mfe_zone_width": "mfe_zone_width",
        "mae_zone_width": "mae_zone_width",
    }

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path.resolve()

    def _connect(self) -> sqlite3.Connection:
        if not self.database_path.is_file():
            raise FileNotFoundError(
                f"Historical Evidence artifact not found: {self.database_path.name}"
            )
        connection = sqlite3.connect(
            f"file:{self.database_path.as_posix()}?mode=ro&immutable=1",
            uri=True,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")
        return connection

    @lru_cache(maxsize=1)
    def _metadata(self) -> tuple[tuple[str, Any], ...]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT key, value FROM metadata ORDER BY key"
            ).fetchall()
        result: list[tuple[str, Any]] = []
        for row in rows:
            try:
                value = json.loads(row["value"])
            except json.JSONDecodeError:
                value = row["value"]
            result.append((row["key"], value))
        return tuple(result)

    def metadata(self) -> dict[str, Any]:
        """Return immutable artifact metadata without reopening SQLite."""

        return dict(self._metadata())

    @staticmethod
    def _where(filters: HistoricalEvidenceFilters) -> tuple[str, list[Any]]:
        clauses: list[str] = []
        values: list[Any] = []
        fields = (
            ("timeframe", filters.timeframe),
            ("zone_type", filters.zone_type),
            ("pattern", filters.pattern),
            ("zone_quality_label", filters.zone_quality_label),
            ("trade_confidence_label", filters.trade_confidence_label),
            ("planning_year", filters.year),
            ("symbol", filters.symbol),
        )
        for field, value in fields:
            if value is not None:
                clauses.append(f"{field} = ?")
                values.append(value)
        if filters.interaction_status == "INTERACTED":
            clauses.append("interacted = 1")
        elif filters.interaction_status == "NOT_INTERACTED":
            clauses.append("interacted = 0")
        return (" WHERE " + " AND ".join(clauses) if clauses else "", values)

    def summary(self, filters: HistoricalEvidenceFilters) -> dict[str, Any]:
        """Return a copy of a version-safe immutable cohort aggregation."""

        return dict(self._summary(filters))

    @lru_cache(maxsize=512)
    def _summary(self, filters: HistoricalEvidenceFilters) -> dict[str, Any]:
        where, values = self._where(filters)
        sql = f"""
            SELECT
              COUNT(*) AS historical_zones,
              SUM(interacted) AS interacted_zones,
              SUM(CASE WHEN interacted=1 AND mfe_zone_width>=1 THEN 1 ELSE 0 END) AS reaction_1,
              SUM(CASE WHEN interacted=1 AND mfe_zone_width>=2 THEN 1 ELSE 0 END) AS reaction_2,
              SUM(CASE WHEN interacted=1 AND mfe_zone_width>=3 THEN 1 ELSE 0 END) AS reaction_3,
              SUM(CASE WHEN interacted=1 AND mfe_zone_width>=5 THEN 1 ELSE 0 END) AS reaction_5,
              SUM(CASE WHEN interacted=1 AND structural_failure=0 THEN 1 ELSE 0 END) AS survived,
              SUM(CASE WHEN interacted=1 AND target_available=1 THEN 1 ELSE 0 END) AS target_available,
              SUM(CASE WHEN interacted=1 AND target_available=1 AND target_achieved=1 THEN 1 ELSE 0 END) AS target_achieved
            FROM historical_zones{where}
        """
        with self._connect() as connection:
            row = dict(connection.execute(sql, values).fetchone())
            mfe = self._median(connection, "mfe_zone_width", where, values)
            mae = self._median(connection, "mae_zone_width", where, values)
        return {key: int(value or 0) for key, value in row.items()} | {
            "median_mfe_zone_width": mfe,
            "median_mae_zone_width": mae,
        }

    @staticmethod
    def _median(
        connection: sqlite3.Connection,
        column: str,
        where: str,
        values: list[Any],
    ) -> float | None:
        interaction = " WHERE interacted = 1 AND "
        suffix = where.removeprefix(" WHERE ") if where else ""
        condition = (
            f"{interaction}{suffix + ' AND ' if suffix else ''}{column} IS NOT NULL"
        )
        # Keep median work inside SQLite.  The previous implementation copied
        # every matching value into Python and sorted it while holding the GIL.
        # During an NSE 500 scan that made otherwise independent read requests
        # compete with canonical scanner CPU work.  SQLite executes this query
        # in native code and the immutable cohort result is cached above.
        row = connection.execute(
            f"""
            SELECT ROUND(AVG(value), 4)
            FROM (
              SELECT
                {column} AS value,
                ROW_NUMBER() OVER (ORDER BY {column}) AS row_number,
                COUNT(*) OVER () AS row_count
              FROM historical_zones{condition}
            )
            WHERE row_number IN ((row_count + 1) / 2, (row_count + 2) / 2)
            """,
            values,
        ).fetchone()
        return float(row[0]) if row and row[0] is not None else None

    def zones(
        self,
        filters: HistoricalEvidenceFilters,
        *,
        page: int,
        page_size: int,
        sort_by: str,
        sort_direction: str,
    ) -> tuple[int, list[dict[str, Any]]]:
        where, values = self._where(filters)
        sort_column = self.SORT_COLUMNS[sort_by]
        direction = "DESC" if sort_direction == "desc" else "ASC"
        with self._connect() as connection:
            total = connection.execute(
                f"SELECT COUNT(*) FROM historical_zones{where}", values
            ).fetchone()[0]
            rows = connection.execute(
                f"SELECT * FROM historical_zones{where} "
                f"ORDER BY {sort_column} {direction}, zone_id ASC LIMIT ? OFFSET ?",
                [*values, page_size, (page - 1) * page_size],
            ).fetchall()
        return int(total), [dict(row) for row in rows]
