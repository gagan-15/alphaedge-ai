"""
Alert validator.

Sprint:
    2.44 - Alert Engine
"""

from backend.config.alert_config import (
    AlertConfig,
)


class AlertValidator:
    """
    Validator for the Alert Engine.
    """

    @staticmethod
    def validate_config(
        config: AlertConfig,
    ) -> None:
        """
        Validate Alert configuration.
        """

        if not config.require_message and (config.default_priority is None):
            raise ValueError("Default priority must be provided.")
