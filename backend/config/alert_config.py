"""
Alert configuration.

Sprint:
    2.44 - Alert Engine
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AlertConfig:
    """
    Configuration for the Alert Engine.
    """

    from backend.models.alert.alert_priority import (
        AlertPriority,
    )

    default_priority: AlertPriority = AlertPriority.MEDIUM

    require_message: bool = True
