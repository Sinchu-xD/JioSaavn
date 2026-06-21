from __future__ import annotations

import re

from .. import endpoints
from ..Core.Request import Request
from ..Formatter.Artist import format_artist
from .Lyrics import get_lyrics

_ID_RE = re.compile(r"^[0-9]{1,20}$")


async def get_artist(
    artist_id: str,
    *,
    n_song: int = 10,
    n_album: int = 10,
    lyrics: bool = False,
    client=None,
) -> dict | None:
    """
    Fetch an artist's full profile page.

    JioSaavn's API requires a **numeric** artist ID (e.g. ``"459320"``).
    You can get this ID from :func:`~JioSaavn.search_artists`.

    Parameters
    ----------
    artist_id : str
        Numeric JioSaavn artist ID (e.g. ``"459320"``).
        Use :func:`search_artists` to find IDs by name.
    n_song : int
        Number of top songs to include (default 10).
    n_album : int
        Number of top albums to include (default 10).
    lyrics : bool
        If ``True``, fetch lyrics for every top song that has them.
    client : JioSaavnClient | None
        Optional shared session client.

    Returns
    -------
    dict | None
        Formatted artist profile, or ``None`` if not found.

    Example
    -------
    >>> from JioSaavn import search_artists, get_artist
    >>>
    >>> # Step 1: find the numeric ID
    >>> results = await search_artists("Arijit Singh", limit=1)
    >>> artist_id = results[0]["id"]   # e.g. "459320"
    >>>
    >>> # Step 2: fetch full profile
    >>> artist = await get_artist(artist_id)
    >>> print(artist["name"], artist["follower_count"])
    """
    if not artist_id or not str(artist_id).strip():
        raise ValueError("artist_id must not be empty")

    artist_id = str(artist_id).strip()
    if not _ID_RE.match(artist_id):
        raise ValueError(
            f"artist_id must be a numeric ID (e.g. '459320'), got: {artist_id!r}. "
            "Use search_artists() to find the numeric ID for an artist name."
        )

    url = (
        endpoints.ARTIST_BY_ID
        + artist_id
        + f"&n_song={n_song}&n_album={n_album}&page=0"
    )

    if client:
        data = await client.get(url)
    else:
        async with Request() as req:
            data = await req.get(url)

    if not data or "error" in data:
        return None

    lyrics_func = get_lyrics if lyrics else None
    return await format_artist(data, lyrics_func)


async def get_artist_top_songs(
    artist_id: str,
    *,
    page: int = 1,
    category: str = "popularity",
    sort_order: str = "desc",
    lyrics: bool = False,
    client=None,
) -> list[dict]:
    """
    Fetch paginated top songs for an artist (requires numeric ID).

    Parameters
    ----------
    artist_id : str
        Numeric JioSaavn artist ID.
    page : int
        Page number (1-indexed).
    category : str
        ``"popularity"`` (default), ``"latest"``, or ``"alphabetical"``.
    sort_order : str
        ``"asc"`` or ``"desc"`` (default).
    lyrics : bool
        Fetch lyrics for each song.
    """
    artist_id = str(artist_id).strip()
    if not _ID_RE.match(artist_id):
        raise ValueError(f"artist_id must be a numeric ID, got: {artist_id!r}")

    url = (
        endpoints.ARTIST_TOP_SONGS
        + artist_id
        + f"&page={page}&category={category}&sort_order={sort_order}"
    )

    if client:
        data = await client.get(url)
    else:
        async with Request() as req:
            data = await req.get(url)

    if not data or "error" in data:
        return []

    from ..Formatter.Song import format_song
    from .Lyrics import get_lyrics as _gl

    songs_raw = (data.get("topSongs") or {}).get("songs") or data.get("songs") or data.get("data") or []
    lyrics_func = _gl if lyrics else None

    results = []
    for s in songs_raw:
        if isinstance(s, dict):
            results.append(await format_song(s, lyrics_func))
    return results


async def get_artist_top_albums(
    artist_id: str,
    *,
    page: int = 1,
    category: str = "latest",
    sort_order: str = "desc",
    client=None,
) -> list[dict]:
    """
    Fetch paginated top albums for an artist (requires numeric ID).

    Parameters
    ----------
    artist_id : str
        Numeric JioSaavn artist ID.
    page : int
        Page number (1-indexed).
    category : str
        ``"latest"`` (default) or ``"alphabetical"``.
    sort_order : str
        ``"asc"`` or ``"desc"`` (default).
    """
    artist_id = str(artist_id).strip()
    if not _ID_RE.match(artist_id):
        raise ValueError(f"artist_id must be a numeric ID, got: {artist_id!r}")

    url = (
        endpoints.ARTIST_TOP_ALBUMS
        + artist_id
        + f"&page={page}&category={category}&sort_order={sort_order}"
    )

    if client:
        data = await client.get(url)
    else:
        async with Request() as req:
            data = await req.get(url)

    if not data or "error" in data:
        return []

    from ..Formatter.Artist import _format_album_brief

    albums_raw = (data.get("topAlbums") or {}).get("albums") or data.get("albums") or data.get("data") or []
    return [_format_album_brief(a) for a in albums_raw if isinstance(a, dict)]
