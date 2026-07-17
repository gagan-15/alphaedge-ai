"""
Tests for Alert Engine.

Sprint:
    2.44 - Alert Engine
"""

import pytest

from backend.config.alert_config import (
    AlertConfig,
)
from backend.engines.alert.alert_engine import (
    AlertEngine,
)
from backend.models.alert.alert_priority import (
    AlertPriority,
)
from backend.models.alert.alert_result import (
    AlertResult,
)


def test_engine_initializes() -> None:
    """
    Engine initializes successfully.
    """

    engine = AlertEngine(
        AlertConfig(),
    )

    assert engine is not None


def test_create_alert_returns_result() -> None:
    """
    Alert creation returns AlertResult.
    """

    engine = AlertEngine(
        AlertConfig(),
    )

    result = engine.create_alert(
        title="High Confidence BUY",
        message="INFY generated a high-confidence BUY signal.",
        requires_action=True,
    )

    assert isinstance(
        result,
        AlertResult,
    )

    assert result.title == "High Confidence BUY"
    assert result.priority == AlertPriority.MEDIUM
    assert result.requires_action is True


def test_custom_priority() -> None:
    """
    Custom priority is respected.
    """

    engine = AlertEngine(
        AlertConfig(),
    )

    result = engine.create_alert(
        title="Critical Risk",
        message="Portfolio risk threshold exceeded.",
        requires_action=True,
        priority=AlertPriority.CRITICAL,
    )

    assert result.priority == AlertPriority.CRITICAL


def test_empty_message_rejected() -> None:
    """
    Empty message is rejected when required.
    """

    engine = AlertEngine(
        AlertConfig(
            require_message=True,
        ),
    )

    with pytest.raises(ValueError):
        engine.create_alert(
            title="Invalid Alert",
            message="   ",
            requires_action=False,
        )


def test_empty_message_allowed() -> None:
    """
    Empty message is allowed when configured.
    """

    engine = AlertEngine(
        AlertConfig(
            require_message=False,
        ),
    )

    result = engine.create_alert(
        title="Silent Alert",
        message="",
        requires_action=False,
    )

    assert result.message == ""
