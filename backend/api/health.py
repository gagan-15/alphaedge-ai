"""
Health API.

Sprint:
    2.48 - Dashboard Service Enhancement
"""

from fastapi import APIRouter

from backend.api.models.health_response import (
    HealthResponse,
)

health_router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@health_router.get(
    "/",
    response_model=HealthResponse,
)
def health() -> HealthResponse:
    """
    Health check endpoint.
    """

    return HealthResponse(
        status="healthy",
    )
