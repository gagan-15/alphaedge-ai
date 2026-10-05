"""Frozen provider-source semantics for persistent scanner candles."""

from __future__ import annotations


DAILY_SOURCE_SEMANTICS_VERSION = "yahoo-adjusted-daily-v1"
DAILY_HISTORY_PERIOD = "10y"
DAILY_SOURCE_INTERVAL = "1d"

# Yahoo's current adjusted-price behavior was already used implicitly by the
# project. Pinning it makes persistence reproducible without changing prices.
YAHOO_AUTO_ADJUST = True
INCLUDE_INCOMPLETE_CURRENT_PERIOD = True
