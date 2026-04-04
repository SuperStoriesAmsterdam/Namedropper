"""Standard error response model and global exception handler.

All API errors return the same JSON shape: {code, message, detail?}.
This makes frontend error handling predictable across all endpoints.
"""

import logging
from typing import Optional

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ErrorResponse(BaseModel):
    """Standard error response returned by all endpoints."""

    code: str
    message: str
    detail: Optional[str] = None


async def api_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch unhandled exceptions and return a consistent error shape."""
    logger.exception(f"Unhandled exception on {request.method} {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"code": "INTERNAL_ERROR", "message": "Something went wrong."},
    )
