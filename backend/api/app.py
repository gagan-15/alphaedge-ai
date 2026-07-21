"""
FastAPI Application.

Sprint:
    2.56 - CORS Middleware
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.exception_handler import (
    register_exception_handlers,
)
from backend.api.router import (
    api_router,
)

app = FastAPI(
    title="AlphaEdge AI",
    version="0.3.0",
    description="AI-assisted Trading Intelligence Platform.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(
    app,
)

app.include_router(
    api_router,
)