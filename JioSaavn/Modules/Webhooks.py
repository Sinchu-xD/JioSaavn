"""Webhook notifier — fire HTTP callbacks when followed artists drop new music."""
from __future__ import annotations
import asyncio
import json
from pathlib import Path
from typing import Any
import aiohttp


class WebhookNotifier:
    def __init__(self, state_path: str = "saavn_webhooks.json"):
        self.state_path = Path(state_path)
        self._state: dict = json.loads(self.state_path.read_text()) if self.state_path.exists() else {}

    def _save(self) -> None:
        self.state_path.write_text(json.dumps(self._state, indent=2, default=str))

    def subscribe(self, artist_id: str, webhook_url: str) -> None:
        self._state.setdefault("subs", {}).setdefault(artist_id, [])
        if webhook_url not in self._state["subs"][artist_id]:
            self._state["subs"][artist_id].append(webhook_url)
        self._save()

    def unsubscribe(self, artist_id: str, webhook_url: str) -> None:
        self._state.get("subs", {}).get(artist_id, []).remove(webhook_url)
        self._save()

    async def poll_once(self, client: Any) -> int:
        """Check every subscribed artist for new songs and fire webhooks. Returns # fired."""
        fired = 0
        subs = self._state.get("subs", {})
        seen: dict = self._state.setdefault("seen", {})
        async with aiohttp.ClientSession() as session:
            for artist_id, urls in list(subs.items()):
                try:
                    songs = await client.get_artist_songs(artist_id)
                except Exception:
                    continue
                current = {s.get("id") or s.get("songid") for s in (songs or [])}
                previous = set(seen.get(artist_id, []))
                new_ids = current - previous
                seen[artist_id] = list(current)
                for sid in new_ids:
                    payload = {"event": "new_song", "artist_id": artist_id, "song_id": sid}
                    for url in urls:
                        try:
                            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as r:
                                if 200 <= r.status < 300:
                                    fired += 1
                        except Exception:
                            pass
        self._save()
        return fired

    async def run_forever(self, client: Any, interval_seconds: int = 3600) -> None:
        while True:
            await self.poll_once(client)
            await asyncio.sleep(interval_seconds)
