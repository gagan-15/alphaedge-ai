"""
FastAPI Application.

Sprint:
    2.46 - FastAPI Foundation
"""

from fastapi import FastAPI

from backend.api.router import (
    api_router,
)

app = FastAPI(
    title="AlphaEdge AI",
    version="0.2.23",
    description=("AI-assisted Trading Intelligence Platform."),
)

app.include_router(api_router)
