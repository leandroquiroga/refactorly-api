from __future__ import annotations

import structlog
from fastapi import Request
from collections.abc import AsyncGenerator
from app.domain import InvalidCodeError, LLMProviderError, ReviewRequest
from app.application import ReviewService

logger = structlog.get_logger(__name__)


async def stream_review(
    request: Request,
    body: ReviewRequest,
    service: ReviewService,
) -> AsyncGenerator[dict[str, str], None]:
    try:
        # prevents token burning when the client disconnects
        async for chunk in service.review_stream(body):
            if await request.is_disconnected():
                logger.info("client_disconnected", path="/api/review")
                return
            yield {"event": "chunk", "data": chunk}
        yield {"event": "done", "data": ""}
    except LLMProviderError as exc:
        yield {"event": "error", "data": str(exc)}
    except InvalidCodeError as exc:
        yield {"event": "error", "data": str(exc)}
