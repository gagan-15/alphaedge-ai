"""
Multi Rule Validator for AlphaEdge AI.

Sprint:
    2.24 - Multi Rule Engine
"""

from backend.models.rule import Rule


class MultiRuleValidator:
    """
    Validator for Multi Rule Engine inputs.
    """

    @staticmethod
    def validate_rules(rules: list[Rule]) -> None:
        """
        Validate the rule collection.
        """

        if rules is None:
            raise ValueError("Rules cannot be None.")

        if not isinstance(rules, list):
            raise TypeError("Rules must be a list.")

        if not rules:
            raise ValueError("Rules cannot be empty.")

        for rule in rules:
            if not isinstance(rule, Rule):
                raise TypeError("Every item must be a Rule.")
