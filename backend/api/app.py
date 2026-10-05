"""
FastAPI Application.

Sprint:
    2.56 - CORS Middleware
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.exception_handler import (
    register_exception_handlers,
)
from backend.api.router import (
    api_router,
)
from backend.api.scanner import start_core_timeframe_preparation
from backend.config.market_data_providers import MARKET_DATA_PROVIDER
from backend.services.scanner.instrument_master_service import (
    start_instrument_master_synchronization,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Resume persistent preparation without tying it to a request."""

    # Dhan production serves only persisted READY snapshots. Its scheduled
    # incremental updater owns all Dhan refresh/materialization work; startup
    # must never trigger the legacy Yahoo-oriented preparation path.
    if MARKET_DATA_PROVIDER == "dhan":
        yield
        return
    sync_future = start_instrument_master_synchronization()
    # Materialization must resolve the universe only after the atomic master
    # synchronization attempt completes. A failed refresh still preserves and
    # prepares the last-known-good membership.
    sync_future.add_done_callback(
        lambda _: start_core_timeframe_preparation()
    )
    yield

app = FastAPI(
    title="AlphaEdge AI",
    version="0.3.0",
    description="AI-assisted Trading Intelligence Platform.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
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
