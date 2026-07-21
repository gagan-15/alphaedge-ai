"""
Global Exception Handler.

Sprint:
    2.49 - Exception Handling
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.core.exceptions import (
    AlphaEdgeAIException,
)


def register_exception_handlers(
    app: FastAPI,
) -> None:
    """
    Register global exception handlers.
    """

    @app.exception_handler(
        AlphaEdgeAIException,
    )
    async def handle_alphaedge_exception(
        request: Request,
        exception: AlphaEdgeAIException,
    ) -> JSONResponse:
        """
        Handle AlphaEdge AI exceptions.
        """

        return JSONResponse(
            status_code=400,
            content={
                "error": type(exception).__name__,
                "message": str(exception),
                "path": str(request.url.path),
            },
        )
