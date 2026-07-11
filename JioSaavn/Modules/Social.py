"""Social / metadata — credits, release calendar, artist comparison."""
from __future__ import annotations
from typing import Any


async def get_song_credits(client: Any, song_id: str) -> dict:
    """Extract composer / lyricist / producer credits from song metadata."""
    song = await client.get_song(song_id)
    if not song:
        return {}
    return {
        "singers": _parse_list(song.get("singers") or song.get("primary_artists")),
        "music": _parse_list(song.get("music") or song.get("music_directors")),
        "lyricists": _parse_list(song.get("lyricists") or song.get("lyricist")),
        "starring": _parse_list(song.get("starring")),
        "label": song.get("label"),
        "release_date": song.get("release_date"),
        "copyright": song.get("copyright_text"),
    }


async def get_release_calendar(client: Any, days_back: int = 30) -> list[dict]:
    """Fetch new releases sorted by release date."""
    try:
        releases = await client.get_new_releases()
    except Exception:
        return []
    return sorted(releases or [], key=lambda s: s.get("release_date", ""), reverse=True)


async def compare_artists(client: Any, artist_id_a: str, artist_id_b: str) -> dict:
    """Side-by-side artist stats."""
    a = await client.get_artist(artist_id_a)
    b = await client.get_artist(artist_id_b)
    return {
        "a": _artist_summary(a),
        "b": _artist_summary(b),
    }


def _artist_summary(a: dict) -> dict:
    if not a:
        return {}
    return {
        "name": a.get("name"),
        "followers": a.get("follower_count") or a.get("fan_count"),
        "top_songs": len(a.get("top_songs") or []),
        "top_albums": len(a.get("top_albums") or []),
        "dominant_language": a.get("dominantLanguage") or a.get("language"),
        "type": a.get("type"),
    }


def _parse_list(v: Any) -> list[str]:
    if not v: return []
    if isinstance(v, list): return [str(x) for x in v]
    return [s.strip() for s in str(v).split(",") if s.strip()]
