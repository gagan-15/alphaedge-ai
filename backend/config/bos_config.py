"""
AlphaEdge AI
--------------

Module:
    backend.config.bos_config

Description:
    Configuration for the Break of Structure (BOS) Engine.

Version:
    v0.2.8

Sprint:
    2.29 - Break of Structure Engine
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class BOSConfig:
    """
    Configuration settings for Break of Structure detection.
    """

    # Swing detection
    swing_left_bars: int = 2
    swing_right_bars: int = 2

    # Break confirmation
    confirmation_source: str = "close"

    # Buffer
    break_buffer_type: str = "percentage"
    break_buffer_value: float = 0.0

    # Rules
    minimum_bars_after_swing: int = 1
    allow_equal_break: bool = False
    deduplicate_events: bool = True

    # Logging
    enable_logging: bool = True

    # Validation
    validate_inputs: bool = True
