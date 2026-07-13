"""
File Name:
    settings.py

Purpose:
    Centralized configuration for AlphaEdge AI.

Description:
    This file contains application-wide configuration
    values that are shared across multiple modules.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

# ==========================================================
# Application Information
# ==========================================================

APP_NAME = "AlphaEdge AI"

VERSION = "0.2.5"

# ==========================================================
# Market Data Configuration
# ==========================================================

DEFAULT_PROVIDER = "Yahoo"

DEFAULT_SYMBOL = "TCS.NS"

DEFAULT_PERIOD = "1y"

DEFAULT_INTERVAL = "1d"

RSI_NEUTRAL_LEVEL = 50

# ==========================================================
# Zone Detection Configuration
# Sprint 2.26
# ==========================================================

# Minimum number of consecutive base candles.
MIN_BASE_CANDLES = 1

# Maximum number of consecutive base candles.
MAX_BASE_CANDLES = 3

# Maximum allowed candle body percentage
# relative to the total candle range.
#
# Formula:
# abs(Close - Open) / (High - Low) * 100
#
# Example:
# Body = 2
# Range = 5
# Body % = 40%
#
# A candle qualifies as a base candle when:
# Body % <= MAX_BASE_BODY_PERCENT
MAX_BASE_BODY_PERCENT = 50.0

# ==========================================================
# Departure Detection Configuration
# Sprint 2.26
# ==========================================================

# Minimum multiplier that the departure candle range
# must exceed relative to the average base candle range.
MIN_DEPARTURE_RANGE_MULTIPLIER = 1.0
