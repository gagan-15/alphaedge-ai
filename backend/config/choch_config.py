"""
Configuration for the Change of Character (CHoCH) Engine.

Sprint:
    2.30 - Change of Character Engine
"""

from dataclasses import dataclass


@dataclass(slots=True)
class CHoCHConfig:
    """
    Configuration options for CHoCH detection.
    """

    confirmation_source: str = "close"

    break_buffer_type: str = "percentage"

    break_buffer_value: float = 0.0

    allow_equal_break: bool = False

    minimum_structure_points: int = 4
