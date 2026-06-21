from __future__ import annotations

from .. import endpoints
from ..Core.Request import Request
from ..Utils.Text import clean


def _format_trending_item(item: dict) -> dict:
    """Format a mini trending item (can be a song, album, or playlist)."""
    more = item.get("more_info") or {}
    artists_map = more.get("artistMap") or {}
    primary = artists_map.get("primary_artists") or []
    primary_artists = ", ".join(
        a.get("name", "") for a in primary if isinstance(a, dict)
    )
    return {
        "id": item.get("id"),
        "title": clean(item.get("title")),
        "type": item.get("type"),
        "image": (item.get("image") or "").replace("150x150", "500x500"),
        "language": item.get("language"),
        "year": item.get("year"),
        "play_count": item.get("play_count"),
        "release_date": more.get("release_date"),
        "song_count": more.get("song_count"),
        "primary_artists": primary_artists,
        "perma_url": item.get("perma_url"),
    }


async def _get_launch_data(client=None) -> dict:
    if client:
        data = await client.get(endpoints.LAUNCH_DATA)
    else:
        async with Request() as req:
            data = await req.get(endpoints.LAUNCH_DATA)
    return data or {}


async def get_trending(
    *,
    language: str | list[str] | None = None,
    limit: int = 20,
    client=None,
) -> list[dict]:
    """
    Fetch currently trending songs and albums on JioSaavn.

    Returns items from JioSaavn's ``new_trending`` feed, which contains a
    mix of recently trending songs and newly released albums.

    Parameters
    ----------
    language : str | list[str] | None
        Filter by language (e.g. ``"hindi"``, ``["hindi", "english"]``).
        ``None`` returns all languages.
    limit : int
        Maximum number of results (default 20).
    client : JioSaavnClient | None
        Optional shared session client.

    Returns
    -------
    list[dict]
        List of trending item dicts with ``id``, ``title``, ``type``
        (``"song"`` or ``"album"``), ``image``, ``language``,
        ``primary_artists``, ``release_date``.

    Example
    -------
    >>> items = await get_trending(language="hindi", limit=10)
    >>> for item in items:
    ...     print(item["title"], f"({item['type']})")
    """
    limit = max(1, min(limit, 50))
    launch = await _get_launch_data(client=client)

    items = launch.get("new_trending") or []
    if not isinstance(items, list):
        return []

    if language:
        langs = {language.lower()} if isinstance(language, str) else {l.lower() for l in language}
        items = [i for i in items if (i.get("language") or "").lower() in langs]

    return [_format_trending_item(i) for i in items[:limit] if isinstance(i, dict)]


async def get_new_releases(
    *,
    language: str | list[str] | None = None,
    limit: int = 20,
    client=None,
) -> list[dict]:
    """
    Fetch newly released albums from JioSaavn.

    Parameters
    ----------
    language : str | list[str] | None
        Optional language filter (e.g. ``"hindi"``, ``"english"``).
    limit : int
        Maximum number of albums (default 20).
    client : JioSaavnClient | None
        Optional shared session client.

    Returns
    -------
    list[dict]
        List of album summary dicts with ``id``, ``title``, ``image``,
        ``language``, ``release_date``, ``song_count``.

    Example
    -------
    >>> albums = await get_new_releases(language="punjabi", limit=10)
    >>> for a in albums:
    ...     print(a["title"], a["release_date"])
    """
    limit = max(1, min(limit, 50))
    launch = await _get_launch_data(client=client)

    items = launch.get("new_albums") or []
    if not isinstance(items, list):
        return []

    if language:
        langs = {language.lower()} if isinstance(language, str) else {l.lower() for l in language}
        items = [i for i in items if (i.get("language") or "").lower() in langs]

    return [_format_trending_item(i) for i in items[:limit] if isinstance(i, dict)]


async def get_top_searches(
    *,
    limit: int = 10,
    client=None,
) -> list[str]:
    """
    Fetch the current top search queries on JioSaavn.

    Parameters
    ----------
    limit : int
        Maximum number of search terms to return (default 10).
    client : JioSaavnClient | None
        Optional shared session client.

    Returns
    -------
    list[str]
        List of top search term strings, e.g.
        ``["Arijit Singh", "Pritam", "Bollywood Hits", ...]``.

    Example
    -------
    >>> terms = await get_top_searches(limit=10)
    >>> for t in terms:
    ...     print(t)
    """
    limit = max(1, min(limit, 50))

    if client:
        data = await client.get(endpoints.TOP_SEARCHES)
    else:
        async with Request() as req:
            data = await req.get(endpoints.TOP_SEARCHES)

    if not data:
        return []

    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = data.get("data") or data.get("results") or []
    else:
        return []

    terms: list[str] = []
    for item in items[:limit]:
        if isinstance(item, str):
            terms.append(item)
        elif isinstance(item, dict):
            name = item.get("title") or item.get("query") or item.get("name")
            if name:
                terms.append(clean(name))

    return terms


async def get_modules(
    *,
    language: str | None = None,
    limit: int = 10,
    client=None,
) -> dict:
    """
    Fetch all JioSaavn homepage modules in a single API call.

    Returns trending items, new releases, charts, and featured playlists
    simultaneously — useful when you need to populate a home screen or
    dashboard without multiple separate requests.

    Parameters
    ----------
    language : str | None
        Optional language filter applied to all modules.
    limit : int
        Maximum items per module (default 10).
    client : JioSaavnClient | None
        Optional shared session client.

    Returns
    -------
    dict
        ``{ "trending": [...], "new_releases": [...],
            "charts": [...], "featured_playlists": [...] }``

    Example
    -------
    >>> modules = await get_modules(language="hindi", limit=5)
    >>> for item in modules["trending"]:
    ...     print(item["title"])
    """
    limit = max(1, min(limit, 50))
    launch = await _get_launch_data(client=client)

    def _filter(items: list, lang: str | None) -> list:
        if not lang:
            return items
        lc = lang.lower()
        return [i for i in items if (i.get("language") or "").lower() == lc]

    def _fmt(items: list) -> list:
        return [_format_trending_item(i) for i in items if isinstance(i, dict)]

    trending_raw  = launch.get("new_trending") or []
    releases_raw  = launch.get("new_albums") or []
    charts_raw    = launch.get("charts") or []
    featured_raw  = launch.get("top_playlists") or []

    if language:
        trending_raw = _filter(trending_raw, language)
        releases_raw = _filter(releases_raw, language)

    def _fmt_playlist(items: list) -> list:
        result = []
        for p in items:
            if not isinstance(p, dict):
                continue
            result.append({
                "id": p.get("id"),
                "title": clean(p.get("title") or p.get("listname")),
                "type": p.get("type", "playlist"),
                "image": (p.get("image") or "").replace("150x150", "500x500"),
                "language": p.get("language"),
                "song_count": (p.get("more_info") or {}).get("song_count") or p.get("song_count"),
                "follower_count": p.get("follower_count"),
                "perma_url": p.get("perma_url"),
            })
        return result

    return {
        "trending":           _fmt(trending_raw[:limit]),
        "new_releases":       _fmt(releases_raw[:limit]),
        "charts":             _fmt_playlist(charts_raw[:limit]),
        "featured_playlists": _fmt_playlist(featured_raw[:limit]),
    }
