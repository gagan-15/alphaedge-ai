"""
Dashboard API.

Sprint:
    2.61 - Signals Panel
"""

from fastapi import APIRouter

from backend.api.models.dashboard_response import (
    DashboardResponse,
)
from backend.services.dashboard.dashboard_service import (
    DashboardService,
)

dashboard_router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)

_dashboard_service = DashboardService()


@dashboard_router.get(
    "/",
    response_model=DashboardResponse,
)
def get_dashboard() -> DashboardResponse:
    """
    Return the complete dashboard data.
    """

    return DashboardResponse.model_validate(
        _dashboard_service.get_dashboard(),
    )