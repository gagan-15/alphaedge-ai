"""
Entry Confirmation Configuration.

Sprint:
    2.37 - Entry Confirmation Engine
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class EntryConfirmationConfig:
    """
    Configuration for Entry Confirmation Engine.
    """

    minimum_confirmation_score: float = 70.0

    require_volume_confirmation: bool = True

    require_trend_confirmation: bool = True

    require_momentum_confirmation: bool = True
