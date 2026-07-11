from __future__ import annotations

import asyncio
import re

from .. import endpoints
from ..Core.Request import Request
from ..Formatter.Song import format_song
from .Lyrics import get_lyrics

_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


async def get_radio(
    song_id: str,
    *,
    limit: int = 10,
    lyrics: bool = False,
    client=None,
) -> list[dict]:
    """
    Create a radio station seeded from a song and return its track list.

    Uses JioSaavn's ``webradio`` API: first creates an entity station seeded
    by the given song ID, then fetches ``limit`` songs from that station.

    Parameters
    ----------
    song_id : str
        JioSaavn song ID to seed the radio (e.g. ``"aRZbUYD7"``).
    limit : int
        Number of radio tracks to return (1–25, default 10).
    lyrics : bool
        If ``True``, fetch lyrics for each track (extra network requests).
    client : JioSaavnClient | None
        Optional shared session client.

    Returns
    -------
    list[dict]
        List of formatted song dicts for the radio station queue.

    Example
    -------
    >>> songs = await search("Tum Hi Ho")
    >>> tracks = await get_radio(songs[0]["id"], limit=10)
    >>> for t in tracks:
    ...     print(t["song"], "—", t["primary_artists"])
    """
    if not song_id or not _ID_RE.match(song_id):
        raise ValueError(f"Invalid song_id: {song_id!r}")

    limit = max(1, min(limit, 25))

    create_url = (
        endpoints.RADIO_CREATE
        + f"&pids={song_id}&k=5&next=1&type=song"
    )

    if client:
        station_data = await client.get(create_url)
    else:
        async with Request() as req:
            station_data = await req.get(create_url)

    if not station_data:
        return []

    station_id = station_data.get("stationid")
    if not station_id:
        return []

    songs_url = (
        endpoints.RADIO_SONGS
        + f"&stationid={station_id}&k={limit}&next=1"
    )

    if client:
        songs_data = await client.get(songs_url)
    else:
        async with Request() as req:
            songs_data = await req.get(songs_url)

    if not songs_data:
        return []

    raw_songs: list[dict] = []
    for key, val in songs_data.items():
        if isinstance(val, dict) and val.get("type") == "song":
            raw = val.get("song") or val
            if isinstance(raw, dict):
                raw_songs.append(raw)

    if not raw_songs:
        return []

    sem = asyncio.Semaphore(5)
    lyrics_func = get_lyrics if lyrics else None

    async def process(s: dict) -> dict | None:
        async with sem:
            try:
                return await format_song(s, lyrics_func)
            except Exception:
                return None

    results = await asyncio.gather(*[process(s) for s in raw_songs[:limit]], return_exceptions=True)
    return [r for r in results if r and not isinstance(r, Exception)]
