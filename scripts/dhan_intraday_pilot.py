"""Run the bounded Dhan intraday pilot; never use this for broad ingestion."""

from __future__ import annotations

import json

from backend.services.market_data.dhan_intraday_pilot_service import (
    DhanIntradayPilotService,
)


if __name__ == "__main__":
    report = DhanIntradayPilotService().run()
    print(json.dumps(report.__dict__, sort_keys=True))
