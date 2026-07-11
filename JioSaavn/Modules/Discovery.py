"""Discovery — daily mix, time machine, regional charts, artist radio."""
from __future__ import annotations
import hashlib
import datetime as dt
from typing import Any


async def daily_mix(client: Any, seed_songs: list[str], size: int = 30) -> list[dict]:
    """Deterministic daily-rotating personalized mix from a set of seeds."""
    today = dt.date.today().isoformat()
    digest = hashlib.md5((today + "|".join(seed_songs)).encode()).digest()
    idx = int.from_bytes(digest[:2], "big") % max(len(seed_songs), 1)
    anchor = seed_songs[idx]
    from .Discovery import _dedupe  # self-ref safe
    picks: list[dict] = []
    seen = set()
    for sid in [anchor, *seed_songs]:
        try:
            sug = await client.get_suggestions(sid, limit=10)
        except Exception:
            continue
        for s in sug or []:
            cid = s.get("id") or s.get("songid")
            if cid and cid not in seen:
                seen.add(cid); picks.append(s)
                if len(picks) >= size:
                    return picks
    return picks


async def time_machine(client: Any, year: int, limit: int = 30) -> list[dict]:
    """Top songs from a specific year (searches by year)."""
    from .AdvSearch import search_filters
    results = await client.search_songs(str(year), limit=limit * 3)
    return search_filters(results or [], year_min=year, year_max=year)[:limit]


async def regional_charts(client: Any, language: str, limit: int = 20) -> list[dict]:
    """Get top charts filtered by language."""
    try:
        charts = await client.get_charts()
    except Exception:
        charts = []
    from .AdvSearch import search_filters
    return search_filters(charts or [], language=language)[:limit]


async def artist_radio(client: Any, artist_id: str, size: int = 30) -> list[dict]:
    """Infinite-style artist radio: top songs + suggestions."""
    try:
        top = await client.get_artist_songs(artist_id)
    except Exception:
        top = []
    top = top or []
    seen = set(); out: list[dict] = []
    for s in top:
        cid = s.get("id") or s.get("songid")
        if cid and cid not in seen:
            seen.add(cid); out.append(s)
    for s in list(top)[:5]:
        try:
            sug = await client.get_suggestions(s.get("id") or s.get("songid"), limit=10)
        except Exception:
            continue
        for x in sug or []:
            cid = x.get("id") or x.get("songid")
            if cid and cid not in seen:
                seen.add(cid); out.append(x)
                if len(out) >= size:
                    return out
    return out[:size]


def _dedupe(items: list[dict]) -> list[dict]:
    seen = set(); out = []
    for i in items:
        k = i.get("id") or i.get("songid")
        if k and k not in seen:
            seen.add(k); out.append(i)
    return out
