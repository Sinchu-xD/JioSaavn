"""Token-bucket async rate limiter for SaavnAPI."""
from __future__ import annotations

import asyncio
import time


class RateLimiter:
    """Token bucket. `rate` tokens per `per` seconds, up to `capacity` burst."""

    def __init__(self, rate: float = 10.0, per: float = 1.0, capacity: float | None = None):
        self.rate = rate
        self.per = per
        self.capacity = capacity if capacity is not None else rate
        self._tokens = self.capacity
        self._updated = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: float = 1.0) -> None:
        while True:
            async with self._lock:
                now = time.monotonic()
                elapsed = now - self._updated
                self._tokens = min(self.capacity, self._tokens + elapsed * (self.rate / self.per))
                self._updated = now
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return
                deficit = tokens - self._tokens
                wait = deficit * (self.per / self.rate)
            await asyncio.sleep(wait)

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, *exc):
        return False


__all__ = ["RateLimiter"]
