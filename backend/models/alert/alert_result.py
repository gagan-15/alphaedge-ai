"""
Alert Result model.

Sprint:
    2.44 - Alert Engine
"""

from dataclasses import dataclass

from backend.models.alert.alert_priority import (
    AlertPriority,
)


@dataclass(frozen=True)
class AlertResult:
    """
    Represents a generated alert.
    """

    title: str

    message: str

    priority: AlertPriority

    requires_action: bool
