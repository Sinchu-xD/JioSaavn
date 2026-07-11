from __future__ import annotations

import re

from .. import endpoints
from ..Core.Request import Request

_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


async def get_lyrics(song_id: str, client=None) -> str | None:
    """
    Fetch lyrics for a song.

    Parameters
    ----------
    song_id : str
        JioSaavn song ID (e.g. ``"4ZSL1xJk"``).
    client : JioSaavnClient | None
        Optional shared session client.

    Returns
    -------
    str | None
        Plain-text lyrics string, or ``None`` if the song has no lyrics
        or the ID is invalid.

    Example
    -------
    >>> lyrics = await get_lyrics("4ZSL1xJk")
    >>> if lyrics:
    ...     print(lyrics[:200])
    """
    if not song_id or not _ID_RE.match(song_id):
        raise ValueError(f"Invalid song_id: {song_id!r}")

    url = endpoints.LYRICS + song_id

    if client:
        data = await client.get(url)
    else:
        async with Request() as req:
            data = await req.get(url)

    if not data:
        return None

    return data.get("lyrics")
