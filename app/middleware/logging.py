from __future__ import annotations

import uuid
import structlog

from collections.abc import Awaitable, Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger()

class RequestIdMiddleware(BaseHTTPMiddleware):
    """Attach a unique request_id to every request for tracing"""
    
    async def dispath(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request_id = str(uuid.uuid4())
        
        structlog.contextvars.bind_contextvars(request_id=request_id)
        request.state.request_id = request_id
        
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else "unknown"
        )
        
        response = await call_next(request)
        
        logger.info(
            "request_finished",
            status_code=response.status_code
        )
        
        structlog.contextvars.clear_contextvars()
        
        return response