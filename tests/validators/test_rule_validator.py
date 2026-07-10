import pytest

from backend.validators.rule_validator import RuleValidator


def test_validate_indicator_results_success():
    """Validation should succeed for a valid dictionary."""

    indicator_results = {
        "rsi": 55
    }

    RuleValidator.validate_indicator_results(
        indicator_results
    )


def test_validate_indicator_results_none():
    """Validation should fail when input is None."""

    with pytest.raises(ValueError):
        RuleValidator.validate_indicator_results(None)


def test_validate_indicator_results_empty():
    """Validation should fail for an empty dictionary."""

    with pytest.raises(ValueError):
        RuleValidator.validate_indicator_results({})


def test_validate_indicator_results_wrong_type():
    """Validation should fail for invalid input types."""

    with pytest.raises(TypeError):
        RuleValidator.validate_indicator_results([])

def test_validate_indicator_results_missing_rsi():
    """Validation should fail when RSI is missing."""

    indicator_results = {
        "macd": 1.2
    }

    with pytest.raises(ValueError):
        RuleValidator.validate_indicator_results(
            indicator_results
        )