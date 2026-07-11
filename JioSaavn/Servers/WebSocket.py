"""WebSocket now-playing broadcaster.

Run:  pip install websockets && python -m JioSaavn.Servers.WebSocket
Clients connect to ws://host:8765 and receive JSON messages when the server
publishes now-playing updates.
"""
from __future__ import annotations
import asyncio
import json
from typing import Set


class NowPlayingHub:
    def __init__(self) -> None:
        self.clients: Set = set()
        self._lock = asyncio.Lock()

    async def register(self, ws) -> None:
        async with self._lock:
            self.clients.add(ws)

    async def unregister(self, ws) -> None:
        async with self._lock:
            self.clients.discard(ws)

    async def broadcast(self, payload: dict) -> None:
        data = json.dumps(payload, ensure_ascii=False, default=str)
        async with self._lock:
            targets = list(self.clients)
        for ws in targets:
            try:
                await ws.send(data)
            except Exception:
                await self.unregister(ws)


hub = NowPlayingHub()


async def _handler(ws) -> None:
    await hub.register(ws)
    try:
        async for msg in ws:
            try:
                data = json.loads(msg)
                if data.get("type") == "now_playing":
                    await hub.broadcast(data)
            except Exception:
                pass
    finally:
        await hub.unregister(ws)


async def main(host: str = "0.0.0.0", port: int = 8765) -> None:
    import websockets  # type: ignore
    async with websockets.serve(_handler, host, port):
        print(f"[SaavnKit WS] listening on ws://{host}:{port}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
