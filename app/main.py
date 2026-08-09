from __future__ import annotations
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from slowapi.middleware import SlowAPIMiddleware

from app.api import router
from app.api.limiter import limiter
from app.config import settings, configure_logging
from app.middleware import SecurityHeadersMiddleware, RequestSizeLimitMiddleware, RequestIdMiddleware


async def _rate_limit_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Convert RateLimitExceeded into a proper 429 JSON response."""
    assert isinstance(exc, RateLimitExceeded)
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."},
    )

configure_logging(settings.LOG_LEVEL)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield


app = FastAPI(
    title="Refactorly API",
    description="Code review copilot powered by LLMs",
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(RequestSizeLimitMiddleware, max_size=settings.MAX_BOY_SIZE)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIdMiddleware) 
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)
