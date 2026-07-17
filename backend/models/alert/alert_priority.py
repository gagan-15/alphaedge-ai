"""
Alert Priority.

Sprint:
    2.44 - Alert Engine
"""

from enum import Enum


class AlertPriority(str, Enum):
    """
    Supported alert priorities.
    """

    LOW = "LOW"

    MEDIUM = "MEDIUM"

    HIGH = "HIGH"

    CRITICAL = "CRITICAL"
