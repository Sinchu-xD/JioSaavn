"""Advanced search — fuzzy, lyric-snippet, and multi-filter."""
from __future__ import annotations
from difflib import SequenceMatcher
from typing import Any, Optional


async def fuzzy_search(client: Any, query: str, limit: int = 10, min_score: float = 0.5) -> list[dict]:
    """Typo-tolerant search: fetch a wider set then re-rank by similarity."""
    results = await client.search_songs(query, limit=max(limit * 3, 30))
    ranked = []
    q = query.lower()
    for s in results or []:
        name = (s.get("name") or s.get("title") or "").lower()
        score = SequenceMatcher(None, q, name).ratio()
        if score >= min_score:
            ranked.append((score, s))
    ranked.sort(key=lambda x: -x[0])
    return [s for _, s in ranked[:limit]]


async def search_by_lyrics(client: Any, snippet: str, limit: int = 5) -> list[dict]:
    """Find songs by a lyric fragment. Best-effort: search then fetch lyrics."""
    hits = await client.search_songs(snippet, limit=limit * 4)
    matches: list[dict] = []
    snip = snippet.lower().strip()
    for s in hits or []:
        sid = s.get("id") or s.get("songid")
        if not sid:
            continue
        try:
            lyr = await client.get_lyrics(sid)
        except Exception:
            continue
        text = (lyr or {}).get("lyrics", "") if isinstance(lyr, dict) else str(lyr or "")
        if snip in text.lower():
            matches.append({**s, "_lyric_match": True})
            if len(matches) >= limit:
                break
    return matches


def search_filters(
    songs: list[dict],
    *,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    language: Optional[str] = None,
    min_duration: Optional[int] = None,
    max_duration: Optional[int] = None,
    explicit: Optional[bool] = None,
) -> list[dict]:
    """Post-filter a song list by common attributes."""
    out = []
    for s in songs:
        try:
            yr = int(s.get("year") or 0)
        except (TypeError, ValueError):
            yr = 0
        try:
            dur = int(s.get("duration") or 0)
        except (TypeError, ValueError):
            dur = 0
        if year_min and yr and yr < year_min: continue
        if year_max and yr and yr > year_max: continue
        if language and (s.get("language") or "").lower() != language.lower(): continue
        if min_duration and dur < min_duration: continue
        if max_duration and dur > max_duration: continue
        if explicit is not None and bool(s.get("explicit")) != explicit: continue
        out.append(s)
    return out
