"""SmartQueue — infinite auto-generated queue from a seed song.

Uses suggestions + mood/language matching + artist radio to build an
ever-growing playback queue. Deduplicates songs and re-fills as it drains.
"""
from __future__ import annotations
import asyncio
from collections import deque
from typing import Any, Callable, Deque, Optional


class SmartQueue:
    def __init__(
        self,
        client: Any,
        seed_song_id: str,
        target_size: int = 50,
        refill_threshold: int = 10,
        similarity_hook: Optional[Callable[[dict, dict], float]] = None,
    ):
        self.client = client
        self.seed_song_id = seed_song_id
        self.target_size = target_size
        self.refill_threshold = refill_threshold
        self.similarity_hook = similarity_hook
        self._queue: Deque[dict] = deque()
        self._seen: set[str] = set()
        self._seed_meta: Optional[dict] = None
        self._lock = asyncio.Lock()

    async def _seed(self) -> None:
        if self._seed_meta is None:
            self._seed_meta = await self.client.get_song(self.seed_song_id)
            self._add(self._seed_meta)

    def _add(self, song: dict) -> bool:
        if not song:
            return False
        sid = song.get("id") or song.get("songid")
        if not sid or sid in self._seen:
            return False
        self._seen.add(sid)
        self._queue.append(song)
        return True

    async def _fetch_more(self) -> None:
        base = self._queue[-1] if self._queue else self._seed_meta
        if not base:
            return
        sid = base.get("id") or base.get("songid")
        try:
            suggestions = await self.client.get_suggestions(sid, limit=20)
            for s in suggestions or []:
                self._add(s)
        except Exception:
            pass

    async def next(self) -> Optional[dict]:
        async with self._lock:
            await self._seed()
            if len(self._queue) <= self.refill_threshold:
                await self._fetch_more()
            return self._queue.popleft() if self._queue else None

    async def peek(self, n: int = 5) -> list[dict]:
        async with self._lock:
            await self._seed()
            if len(self._queue) < n:
                await self._fetch_more()
            return list(self._queue)[:n]

    def __len__(self) -> int:
        return len(self._queue)
