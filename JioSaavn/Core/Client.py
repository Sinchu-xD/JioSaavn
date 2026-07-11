from __future__ import annotations

import aiohttp

from .Request import DEFAULT_TIMEOUT, Request


class JioSaavnClient:
    """
    Reusable async session client for batching multiple API calls efficiently.

    Use this as an async context manager when making several requests in one
    go — it keeps the underlying ``aiohttp`` session open so connections are
    reused instead of opened and closed for every call.

    Example
    -------
    .. code-block:: python

        from JioSaavn import JioSaavnClient, search, get_artist, get_trending

        async with JioSaavnClient() as client:
            songs   = await search("Pritam", limit=10, client=client)
            artist  = await get_artist("arijit-singh", client=client)
            trending = await get_trending(limit=20, client=client)
    """

    def __init__(self, timeout: aiohttp.ClientTimeout = DEFAULT_TIMEOUT):
        self._req = Request(timeout=timeout)

    async def __aenter__(self) -> "JioSaavnClient":
        await self._req.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._req.__aexit__(*args)

    async def get(self, url: str) -> dict | None:
        return await self._req.get(url)
