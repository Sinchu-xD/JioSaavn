import asyncio
import json

import aiohttp

from .Parser import extract_json

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=15, connect=5)


class Request:
    def __init__(self, timeout: aiohttp.ClientTimeout = DEFAULT_TIMEOUT):
        self.session: aiohttp.ClientSession | None = None
        self.timeout = timeout

    async def __aenter__(self) -> "Request":
        self.session = aiohttp.ClientSession(headers=HEADERS, timeout=self.timeout)
        return self

    async def __aexit__(self, *args) -> None:
        if self.session and not self.session.closed:
            await self.session.close()

    async def get(self, url: str) -> dict | None:
        if self.session is None:
            raise RuntimeError(
                "Request must be used as an async context manager: "
                "`async with Request() as req:`"
            )
        try:
            async with self.session.get(url) as res:
                if res.status != 200:
                    return None

                text = await res.text()
                return extract_json(text)

        except (aiohttp.ClientError, asyncio.TimeoutError):
            return None
