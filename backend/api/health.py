"""
Health API.

Sprint:
    2.46 - FastAPI Foundation
"""

from fastapi import APIRouter

health_router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@health_router.get("/")
def health() -> dict[str, str]:
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
    }
