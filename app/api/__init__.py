from __future__ import annotations

from app.api.dependencies import get_review_service
from app.api.router import router
from app.api.limiter import limiter

__all__ = [
    "get_review_service",
    "router",
    "limiter"
]