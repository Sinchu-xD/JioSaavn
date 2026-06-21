from __future__ import annotations

import re

from .. import endpoints
from ..Core.Request import Request
from ..Formatter.Playlist import format_playlist
from .Lyrics import get_lyrics

_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


async def _format_playlist(data: dict) -> dict:
    """Async playlist formatter without lyrics (for URL resolver)."""
    return await format_playlist(data, lyrics_func=None)


async def get_playlist(list_id: str, *, lyrics: bool = False, client=None) -> dict | None:
    """
    Fetch a playlist and all its songs.

    Parameters
    ----------
    list_id : str
        JioSaavn playlist ID.
    lyrics : bool
        If ``True``, fetch lyrics for every track when available.
    client : JioSaavnClient | None
        Optional shared session client.

    Returns
    -------
    dict | None
        Formatted playlist dict with ``id``, ``listname``, ``firstname``,
        ``follower_count``, ``song_count``, and ``songs`` list.

    Example
    -------
    >>> pl = await get_playlist("159144718")
    >>> print(pl["listname"], "—", pl["song_count"], "songs")
    >>> for track in pl["songs"]:
    ...     print(" ", track["song"])
    """
    if not list_id or not _ID_RE.match(list_id):
        raise ValueError(f"Invalid list_id: {list_id!r}")

    url = endpoints.PLAYLIST + list_id

    if client:
        data = await client.get(url)
    else:
        async with Request() as req:
            data = await req.get(url)

    if not data:
        return None

    lyrics_func = get_lyrics if lyrics else None
    return await format_playlist(data, lyrics_func)
