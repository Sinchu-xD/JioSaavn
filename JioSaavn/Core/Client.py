from __future__ import annotations

import functools
import aiohttp

from .Request import DEFAULT_TIMEOUT, Request


# Names of top-level JioSaavn functions to expose as client methods.
# Populated lazily to avoid circular import at module load.
_BOUND_METHOD_NAMES = (
    "search", "search_songs", "search_albums", "search_artists",
    "search_playlists", "search_all",
    "get_song", "get_songs", "get_lyrics", "get_suggestions", "get_radio",
    "get_song_by_url", "get_album_by_url", "get_playlist_by_url",
    "get_album", "get_playlist",
    "get_artist", "get_artist_top_songs", "get_artist_top_albums",
    "get_trending", "get_new_releases", "get_top_searches",
    "get_charts", "get_featured_playlists", "get_modules",
)


class JioSaavnClient:
    """
    Reusable async session client for batching multiple API calls efficiently.

    Every top-level JioSaavn function is also accessible as a method on this
    client (with ``client=self`` automatically supplied), so both call styles
    work interchangeably:

    .. code-block:: python

        async with JioSaavnClient() as c:
            # functional style
            from JioSaavn import search
            a = await search("Pritam", client=c)

            # method style
            b = await c.search("Pritam")
            song = await c.get_song("5WXAlMNt")
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

    # ── Dynamic bridge to top-level API functions ────────────────────────
    def __getattr__(self, name: str):
        if name.startswith("_") or name not in _BOUND_METHOD_NAMES:
            raise AttributeError(name)
        import JioSaavn as _api  # local import to avoid cycle
        fn = getattr(_api, name, None)
        if fn is None:
            raise AttributeError(name)

        @functools.wraps(fn)
        async def _bound(*args, **kwargs):
            kwargs.setdefault("client", self)
            return await fn(*args, **kwargs)

        # cache on the instance so repeated access is cheap
        object.__setattr__(self, name, _bound)
        return _bound

    # Aliases used by mega-pack modules that expect these names
    async def get_artist_songs(self, artist_id: str, *, limit: int = 20):
        import JioSaavn as _api
        return await _api.get_artist_top_songs(artist_id, client=self)
