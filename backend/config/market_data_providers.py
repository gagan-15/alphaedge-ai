"""Explicit production and shadow market-data provider identities."""

from __future__ import annotations

import os

# Yahoo is the dependency-free fallback for test and archive contexts. A
# production Dhan deployment selects Dhan explicitly in its local .env.
MARKET_DATA_PROVIDER = os.getenv("MARKET_DATA_PROVIDER", "yahoo").lower()
SHADOW_MARKET_DATA_PROVIDER = os.getenv("SHADOW_MARKET_DATA_PROVIDER", "dhan").lower()

if MARKET_DATA_PROVIDER not in {"yahoo", "dhan"}:
    raise RuntimeError("MARKET_DATA_PROVIDER must be 'yahoo' or 'dhan'.")
