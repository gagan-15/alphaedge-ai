"""
File Name:
    base_indicator.py

Purpose:
    Define the base class for all technical indicators.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""


class BaseIndicator:
    """
    Base class for all indicators in AlphaEdge AI.
    """

    def calculate(self, data):
        """
        Calculate the indicator.

        This method must be implemented
        by every indicator.
        """
        raise NotImplementedError(
            "Each indicator must implement the calculate() method."
        )
