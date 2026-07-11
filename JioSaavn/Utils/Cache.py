"""Async LRU cache with TTL for SaavnAPI."""
from __future__ import annotations

import asyncio
import time
from collections import OrderedDict
from functools import wraps
from typing import Any, Awaitable, Callable, Hashable


class AsyncTTLCache:
    """Bounded async cache. LRU eviction + per-entry TTL."""

    def __init__(self, maxsize: int = 512, ttl: float = 300.0):
        self.maxsize = maxsize
        self.ttl = ttl
        self._data: OrderedDict[Hashable, tuple[float, Any]] = OrderedDict()
        self._lock = asyncio.Lock()
        self.hits = 0
        self.misses = 0

    async def get(self, key: Hashable) -> Any | None:
        async with self._lock:
            item = self._data.get(key)
            if not item:
                self.misses += 1
                return None
            expires, value = item
            if expires < time.time():
                self._data.pop(key, None)
                self.misses += 1
                return None
            self._data.move_to_end(key)
            self.hits += 1
            return value

    async def set(self, key: Hashable, value: Any, ttl: float | None = None) -> None:
        async with self._lock:
            self._data[key] = (time.time() + (ttl or self.ttl), value)
            self._data.move_to_end(key)
            while len(self._data) > self.maxsize:
                self._data.popitem(last=False)

    async def clear(self) -> None:
        async with self._lock:
            self._data.clear()

    def stats(self) -> dict:
        total = self.hits + self.misses
        return {
            "size": len(self._data),
            "maxsize": self.maxsize,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / total if total else 0.0,
        }


def cached(cache: AsyncTTLCache, key_fn: Callable[..., Hashable] | None = None):
    """Decorator to memoize an async function's result in the given cache."""
    def deco(fn: Callable[..., Awaitable[Any]]):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            key = key_fn(*args, **kwargs) if key_fn else (fn.__name__, args, tuple(sorted(kwargs.items())))
            hit = await cache.get(key)
            if hit is not None:
                return hit
            result = await fn(*args, **kwargs)
            if result is not None:
                await cache.set(key, result)
            return result
        return wrapper
    return deco


__all__ = ["AsyncTTLCache", "cached"]
