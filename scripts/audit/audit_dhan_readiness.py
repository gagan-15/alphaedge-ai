"""Bounded Dhan readiness audit; never reads trading APIs or prints credentials."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from pathlib import Path
from time import perf_counter

import pandas as pd
from dotenv import load_dotenv

from backend.data_providers.dhan import (
    DhanDataError,
    DhanInstrument,
    DhanMarketDataProvider,
)


@dataclass(frozen=True)
class HistoryProbe:
    instrument_id: str
    exchange: str
    security_id: str
    symbol: str
    display_name: str
    isin: str
    series: str
    category: str
    window: str
    status: str
    rows: int
    first: str | None
    last: str | None
    http_status: int | None
    error_code: str | None
    error_message: str | None
    retry_after: str | None
    duplicates: int
    out_of_order: int
    malformed_ohlc: int
    negative_volume: int
    zero_range: int
    unexpected_timestamp: int
    elapsed_ms: float


def evenly(items: list[DhanInstrument], count: int) -> list[DhanInstrument]:
    if len(items) <= count:
        return items
    positions = [
        round(index * (len(items) - 1) / (count - 1)) for index in range(count)
    ]
    return [items[position] for position in positions]


def probe(
    provider: DhanMarketDataProvider,
    instrument: DhanInstrument,
    *,
    start: date,
    window: str,
) -> HistoryProbe:
    started = perf_counter()
    frame = pd.DataFrame()
    http_status = error_code = error_message = retry_after = None
    try:
        frame = provider.download_instrument_data(
            instrument,
            start=start,
            end=date.today(),
            interval="1d",
        )
        status = "SUCCESS" if not frame.empty else "NO_DATA"
    except DhanDataError as error:
        status = "RATE_LIMITED" if error.http_status == 429 else "PROVIDER_ERROR"
        http_status = error.http_status
        error_code = error.error_code
        error_message = str(error)[:300]
        retry_after = error.retry_after
    except Exception as error:
        status = "REQUEST_ERROR"
        error_message = f"{type(error).__name__}: {str(error)[:250]}"

    duplicates = out_of_order = malformed = negative_volume = zero_range = 0
    unexpected_timestamp = 0
    if not frame.empty:
        duplicates = int(frame.index.duplicated().sum())
        out_of_order = int(not frame.index.is_monotonic_increasing)
        malformed = int(
            (
                (frame["High"] < frame["Low"])
                | (frame["Open"] < frame["Low"])
                | (frame["Open"] > frame["High"])
                | (frame["Close"] < frame["Low"])
                | (frame["Close"] > frame["High"])
                | (frame[["Open", "High", "Low", "Close"]] <= 0).any(axis=1)
            ).sum()
        )
        negative_volume = int((frame["Volume"] < 0).sum())
        zero_range = int((frame["High"] == frame["Low"]).sum())
        index = pd.DatetimeIndex(frame.index).tz_convert("Asia/Kolkata")
        unexpected_timestamp = int(
            sum(timestamp.hour != 0 or timestamp.minute != 0 for timestamp in index)
        )
    return HistoryProbe(
        instrument.instrument_id,
        instrument.exchange,
        instrument.security_id,
        instrument.symbol,
        instrument.display_name,
        instrument.isin,
        instrument.series,
        instrument.category,
        window,
        status,
        len(frame),
        str(frame.index.min()) if not frame.empty else None,
        str(frame.index.max()) if not frame.empty else None,
        http_status,
        error_code,
        error_message,
        retry_after,
        duplicates,
        out_of_order,
        malformed,
        negative_volume,
        zero_range,
        unexpected_timestamp,
        round((perf_counter() - started) * 1000, 3),
    )


def summarize(probes: list[HistoryProbe]) -> dict[str, object]:
    return {
        "requested": len(probes),
        "statuses": dict(Counter(item.status for item in probes)),
        "success_percent": round(
            100 * sum(item.status == "SUCCESS" for item in probes) / len(probes), 2
        ),
        "rows": sum(item.rows for item in probes),
        "zero_range": sum(item.zero_range for item in probes),
        "duplicates": sum(item.duplicates for item in probes),
        "out_of_order": sum(item.out_of_order for item in probes),
        "malformed_ohlc": sum(item.malformed_ohlc for item in probes),
        "negative_volume": sum(item.negative_volume for item in probes),
        "unexpected_timestamp": sum(item.unexpected_timestamp for item in probes),
        "elapsed_seconds": round(sum(item.elapsed_ms for item in probes) / 1000, 3),
    }


def main() -> None:
    load_dotenv()
    provider = DhanMarketDataProvider(requests_per_second=4.0)
    master = list(provider.instrument_master(refresh=True))
    by_category = {
        category: sorted(
            (item for item in master if item.category == category),
            key=lambda item: (int(item.security_id), item.symbol),
        )
        for category in ("NSE_MAIN", "NSE_SME", "BSE_MAIN", "BSE_SME")
    }
    nse_isins = {item.isin for item in master if item.exchange == "NSE"}
    bse_cross = [item for item in by_category["BSE_MAIN"] if item.isin in nse_isins]
    bse_only = [item for item in by_category["BSE_MAIN"] if item.isin not in nse_isins]
    bse_sample = evenly(bse_cross, 100) + evenly(bse_only, 100)
    nse_sample = evenly(by_category["NSE_MAIN"], 100) + evenly(
        by_category["NSE_SME"], 100
    )
    original_twenty = by_category["BSE_MAIN"][:20]
    recent_start = date.today() - timedelta(days=366)
    long_start = date.today() - timedelta(days=3660)

    def run(items: list[DhanInstrument], window: str) -> list[HistoryProbe]:
        start = recent_start if window == "recent_1y" else long_start
        return [probe(provider, item, start=start, window=window) for item in items]

    original_long = run(original_twenty, "long_10y")
    original_recent = run(original_twenty, "recent_1y")
    bse_recent = run(bse_sample, "recent_1y")
    bse_long = run(bse_sample, "long_10y")
    nse_recent = run(nse_sample, "recent_1y")
    nse_long = run(nse_sample, "long_10y")

    report = {
        "generated_on": date.today().isoformat(),
        "master_counts": {key: len(value) for key, value in by_category.items()},
        "original_twenty_long": [asdict(item) for item in original_long],
        "original_twenty_recent": [asdict(item) for item in original_recent],
        "summary": {
            "original_20_long": summarize(original_long),
            "original_20_recent": summarize(original_recent),
            "bse_200_recent": summarize(bse_recent),
            "bse_200_long": summarize(bse_long),
            "nse_200_recent": summarize(nse_recent),
            "nse_200_long": summarize(nse_long),
        },
    }
    output = Path("tmp/dhan_readiness_audit.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output), "summary": report["summary"]}, indent=2))


if __name__ == "__main__":
    main()
