"""
API Router.

Sprint:
    2.46 - FastAPI Foundation
"""

from fastapi import APIRouter

from backend.api.auth import (
    auth_router,
)
from backend.api.dashboard import (
    dashboard_router,
)
from backend.api.health import (
    health_router,
)
from backend.api.scanner import (
    scanner_router,
)

api_router = APIRouter()

api_router.include_router(
    auth_router,
)

api_router.include_router(
    health_router,
)

api_router.include_router(
    dashboard_router,
)

api_router.include_router(
    scanner_router,
)
