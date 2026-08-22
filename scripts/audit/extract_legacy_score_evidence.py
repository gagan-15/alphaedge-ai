"""Extract immutable inputs for the real frontend legacy evaluator."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from pandas import concat

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.services.market_data.market_data_service import MarketDataService
from backend.services.market_data.timeframe_service import aggregate_timeframe
from backend.services.scanner.stock_details_analysis_service import (
    StockDetailsAnalysisService,
)


def main() -> None:
    source = Path("tests/fixtures/trade_confidence_nse500_daily_snapshot.json")
    target = Path("tmp/trade7e/legacy-score-inputs.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    snapshot = json.loads(source.read_text(encoding="utf-8"))
    market = MarketDataService()
    details = StockDetailsAnalysisService()
    records = []
    failures = []
    for item in snapshot["results"]:
        try:
            validated = market.get_stock_data_segments(item["symbol"], "1y", "1d")
            data = aggregate_timeframe(concat(validated.segments).sort_index(), item["timeframe"])
            candles = [
                {
                    "time": index.isoformat(),
                    "open": float(row["Open"]), "high": float(row["High"]),
                    "low": float(row["Low"]), "close": float(row["Close"]),
                    "volume": float(row["Volume"]),
                }
                for index, row in data.iterrows()
            ]
            backend = details.build(
                item["symbol"], item["zone_type"], item["proximal_price"],
                item["distal_price"], item["timeframe"],
            )
            records.append({"zone": item, "candles": candles, "backend": backend})
        except Exception as error:
            failures.append({"symbol": item["symbol"], "zone_id": item.get("zone_id"), "reason": type(error).__name__})
    target.write_text(json.dumps({"records": records, "failures": failures}, indent=2), encoding="utf-8")
    print(json.dumps({"records": len(records), "failures": failures}, indent=2))


if __name__ == "__main__":
    main()
