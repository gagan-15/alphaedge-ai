"""
Health Response model.

Sprint:
    2.48 - Dashboard Service Enhancement
"""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """
    Represents the Health API response.
    """

    status: str
