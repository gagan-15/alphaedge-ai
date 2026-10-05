"""
Tests for the Entry Confirmation Validator.
"""

import pytest

from backend.config.entry_confirmation_config import (
    EntryConfirmationConfig,
)
from backend.validators.entry_confirmation_validator import (
    EntryConfirmationValidator,
)


def test_valid_config_is_accepted() -> None:
    """
    A valid confirmation threshold is accepted.
    """

    EntryConfirmationValidator.validate_config(
        EntryConfirmationConfig(),
    )


def test_invalid_confirmation_score_is_rejected() -> None:
    """
    Confirmation score must remain between zero and 100.
    """

    with pytest.raises(ValueError):
        EntryConfirmationValidator.validate_config(
            EntryConfirmationConfig(
                minimum_confirmation_score=101.0,
            ),
        )
