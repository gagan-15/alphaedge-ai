"""Run/resume the approved one-year Dhan NSE 500 intraday materialization."""

from __future__ import annotations

import argparse
import json

from backend.services.market_data.dhan_intraday_nse500_service import (
    DhanIntradayNse500Service,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    report = DhanIntradayNse500Service().run(
        years=1, workers=args.workers, limit=args.limit
    )
    print(json.dumps(report.__dict__, sort_keys=True))


if __name__ == "__main__":
    main()
