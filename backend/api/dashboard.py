"""
Dashboard API.

Sprint:
    2.48 - Dashboard Service Enhancement
"""

from fastapi import APIRouter

from backend.services.dashboard.dashboard_service import (
    DashboardService,
)

dashboard_router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)

_dashboard_service = DashboardService()


@dashboard_router.get("/")
def get_dashboard():
    """
    Return dashboard data.
    """

    return _dashboard_service.get_dashboard()
