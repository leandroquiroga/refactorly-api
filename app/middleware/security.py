from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to every HTTP response"""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        return response
    
class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests with a body exceeding max_size bytes"""
    
    def __init__(self, app, max_size: int = 100_000) -> None:
        super().__init__(app)
        self._max_size = max_size
        
    async def dispatch(self, request: Request, call_next) -> Response:
        content_length = request.headers.get("content-length")
        try:
            too_large = content_length is not None and int(content_length) > self._max_size
        except (TypeError, ValueError):
            # Malformed header: let the request through; Pydantic validation caps the body.
            too_large = False
        if too_large:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request body too large"}
            )
        return await call_next(request)