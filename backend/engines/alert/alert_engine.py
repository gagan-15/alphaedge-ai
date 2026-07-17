"""
Alert Engine.

Sprint:
    2.44 - Alert Engine
"""

from backend.config.alert_config import (
    AlertConfig,
)
from backend.models.alert.alert_priority import (
    AlertPriority,
)
from backend.models.alert.alert_result import (
    AlertResult,
)
from backend.validators.alert_validator import (
    AlertValidator,
)


class AlertEngine:
    """
    Produces alert results.
    """

    def __init__(
        self,
        config: AlertConfig,
    ) -> None:
        """
        Initialize the Alert Engine.
        """
        AlertValidator.validate_config(config)

        self._config = config

    def create_alert(
        self,
        title: str,
        message: str,
        requires_action: bool,
        priority: AlertPriority | None = None,
    ) -> AlertResult:
        """
        Create an alert.
        """

        if priority is None:
            priority = self._config.default_priority

        if self._config.require_message and not message.strip():
            raise ValueError("Alert message cannot be empty.")

        return AlertResult(
            title=title,
            message=message,
            priority=priority,
            requires_action=requires_action,
        )
