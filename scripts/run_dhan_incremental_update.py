"""Run the safe, incremental Dhan EOD update from Task Scheduler or a BAT file."""

from __future__ import annotations

import json
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# CLI, scheduler and desktop launchers use the same ignored local settings.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from backend.services.market_data.dhan_incremental_update_service import (
    DhanIncrementalUpdateService,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume-persisted", action="store_true",
                        help="Recover saved dirty work without contacting Dhan.")
    args = parser.parse_args()
    report = DhanIncrementalUpdateService().run(resume_persisted=args.resume_persisted)
    print(json.dumps({
        "status": report.status,
        "checked": report.checked,
        "changed": report.changed,
        "failed": report.failed,
        "refreshed_timeframes": report.refreshed_timeframes,
        "message": report.message,
    }, sort_keys=True))
    return 0 if report.status in {"READY", "ALREADY_RUNNING"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
