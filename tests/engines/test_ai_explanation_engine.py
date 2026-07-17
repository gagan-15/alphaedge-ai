"""
Tests for AI Explanation Engine.

Sprint:
    2.42 - AI Explanation Engine
"""

import pytest

from backend.config.ai_explanation_config import (
    AIExplanationConfig,
)
from backend.engines.ai_explanation.ai_explanation_engine import (
    AIExplanationEngine,
)
from backend.models.ai_explanation.ai_explanation_result import (
    AIExplanationResult,
)
from backend.models.ai_explanation.explanation_decision import (
    ExplanationDecision,
)


def test_engine_initializes() -> None:
    """
    Engine initializes successfully.
    """

    engine = AIExplanationEngine(
        AIExplanationConfig(),
    )

    assert engine is not None


def test_invalid_configuration() -> None:
    """
    Invalid configuration raises ValueError.
    """

    with pytest.raises(ValueError):
        AIExplanationEngine(
            AIExplanationConfig(
                maximum_reasons=0,
            ),
        )


def test_explanation_result() -> None:
    """
    Explanation is produced successfully.
    """

    engine = AIExplanationEngine(
        AIExplanationConfig(),
    )

    result = engine.explain(
        decision=ExplanationDecision.BUY,
        reasons=[
            "Fresh Weekly Demand",
            "Daily BOS",
            "Strong Volume",
        ],
        confidence_score=91.0,
    )

    assert isinstance(
        result,
        AIExplanationResult,
    )

    assert result.decision == ExplanationDecision.BUY
    assert len(result.reasons) == 3
    assert result.confidence_score == 91.0


def test_maximum_reasons() -> None:
    """
    Maximum reasons are respected.
    """

    engine = AIExplanationEngine(
        AIExplanationConfig(
            maximum_reasons=2,
        ),
    )

    result = engine.explain(
        decision=ExplanationDecision.BUY,
        reasons=[
            "A",
            "B",
            "C",
        ],
        confidence_score=90,
    )

    assert len(result.reasons) == 2


def test_hide_confidence_score() -> None:
    """
    Confidence score can be hidden.
    """

    engine = AIExplanationEngine(
        AIExplanationConfig(
            include_confidence_score=False,
        ),
    )

    result = engine.explain(
        decision=ExplanationDecision.SELL,
        reasons=[
            "Weak Trend",
        ],
        confidence_score=45,
    )

    assert result.confidence_score == 0.0
