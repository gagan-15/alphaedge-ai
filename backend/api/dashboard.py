"""
Dashboard API.

Sprint:
    2.61 - Signals Panel
"""

from fastapi import APIRouter, Query

from backend.api.models.dashboard_response import (
    DashboardResponse,
)
from backend.services.dashboard.dashboard_service import (
    DashboardService,
)
from backend.services.scanner.universe_service import UniverseName

dashboard_router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)

_dashboard_service = DashboardService()


@dashboard_router.get(
    "/",
    response_model=DashboardResponse,
)
def get_dashboard(
    universe: UniverseName = Query(default="nse500"),
    symbols: list[str] | None = Query(default=None),
) -> DashboardResponse:
    """
    Return the complete dashboard data.
    """

    return DashboardResponse.model_validate(
        _dashboard_service.get_dashboard(universe, symbols),
    )
