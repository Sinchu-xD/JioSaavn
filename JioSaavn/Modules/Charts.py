from __future__ import annotations

from .. import endpoints
from ..Core.Request import Request
from ..Utils.Text import clean


async def _get_launch_data(client=None) -> dict:
    if client:
        data = await client.get(endpoints.LAUNCH_DATA)
    else:
        async with Request() as req:
            data = await req.get(endpoints.LAUNCH_DATA)
    return data or {}


def _format_playlist_item(item: dict) -> dict:
    more = item.get("more_info") or {}
    return {
        "id": item.get("id"),
        "name": clean(item.get("title") or item.get("listname")),
        "image": (item.get("image") or "").replace("150x150", "500x500"),
        "song_count": more.get("song_count") or item.get("list_count"),
        "follower_count": more.get("follower_count"),
        "language": item.get("language"),
        "play_count": item.get("play_count"),
        "perma_url": item.get("perma_url"),
    }


async def get_charts(*, client=None) -> list[dict]:
    """
    Fetch JioSaavn's top chart playlists.

    Returns chart playlist summaries. Pass the returned ``id`` to
    :func:`~JioSaavn.get_playlist` to fetch the full song list.

    Parameters
    ----------
    client : JioSaavnClient | None
        Optional shared session client.

    Returns
    -------
    list[dict]
        Each dict contains: ``id``, ``name``, ``image``, ``song_count``,
        ``language``, ``play_count``.

    Example
    -------
    >>> charts = await get_charts()
    >>> for c in charts:
    ...     print(c["name"])
    ...
    >>> # Get songs from the first chart
    >>> from JioSaavn import get_playlist
    >>> playlist = await get_playlist(charts[0]["id"])
    """
    launch = await _get_launch_data(client=client)
    items = launch.get("charts") or []
    if not isinstance(items, list):
        return []
    return [_format_playlist_item(i) for i in items if isinstance(i, dict)]


async def get_featured_playlists(
    *,
    language: str | list[str] | None = None,
    limit: int = 20,
    client=None,
) -> list[dict]:
    """
    Fetch featured / editorial playlists curated by JioSaavn.

    Parameters
    ----------
    language : str | list[str] | None
        Optional language filter (e.g. ``"hindi"``, ``"english"``).
    limit : int
        Maximum results (default 20).
    client : JioSaavnClient | None
        Optional shared session client.

    Returns
    -------
    list[dict]
        List of playlist summary dicts with ``id``, ``name``, ``image``,
        ``song_count``, ``follower_count``.

    Example
    -------
    >>> playlists = await get_featured_playlists(limit=10)
    >>> for p in playlists:
    ...     print(p["name"], "—", p["song_count"], "songs")
    """
    limit = max(1, min(limit, 50))
    launch = await _get_launch_data(client=client)

    items = launch.get("top_playlists") or []
    if not isinstance(items, list):
        return []

    if language:
        langs = {language.lower()} if isinstance(language, str) else {l.lower() for l in language}
        items = [i for i in items if (i.get("language") or "").lower() in langs]

    return [_format_playlist_item(i) for i in items[:limit] if isinstance(i, dict)]
