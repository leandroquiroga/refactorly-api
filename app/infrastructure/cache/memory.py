from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from app.domain import CacheProvider, CodeReview


class MemomyCache(CacheProvider):
    """TTL-based in-memory cache backed by a dict
    Entries older that ttl_seconds are evicted on access
    Set ttl_seconds=0 to disable caching
    """
    
    def __init__(self, ttl_seconds: int = 900) -> None: 
        self._ttl = ttl_seconds
        self._store: dict[str, tuple[CodeReview, datetime]] = {}
        
    async def get(self, key: str) -> CodeReview | None:
        if key not in self._store:
            return None
        
        review, timestamp = self._store[key]
        age = (datetime.now(timezone.utc) - timestamp).total_seconds()
        
        if age > self._ttl:
            del self._store[key]
            return None
        return review
    
    async def set(self, key: str, review: CodeReview) -> None:
        if self._ttl > 0:
            self._store[key] = (review, datetime.now(timezone.utc))
            
    def make_key(self, code: str, language: str | None, response_language: str) -> str:
        raw = f"{code}:{language or ''}"
        return hashlib.sha256(raw.encode()).hexdigest()