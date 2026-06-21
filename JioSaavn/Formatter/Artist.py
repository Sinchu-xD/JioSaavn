from __future__ import annotations

import json as _json

from ..Utils.Text import clean
from .Song import format_song


async def format_artist(data: dict, lyrics_func=None) -> dict:
    image = (data.get("image") or "").replace("150x150", "500x500")

    # Bio is a list of JSON-encoded strings or dicts
    bio_raw = data.get("bio") or []
    bio_text: str | None = None
    parts = []
    for entry in bio_raw:
        if isinstance(entry, str):
            try:
                entry = _json.loads(entry)
            except Exception:
                parts.append(clean(entry))
                continue
        if isinstance(entry, dict):
            text = entry.get("text") or entry.get("p") or ""
            if text:
                parts.append(clean(text))
    bio_text = "\n\n".join(parts) or None

    # topSongs lives under data["topSongs"]["songs"] (not ["data"])
    top_songs_raw = (data.get("topSongs") or {}).get("songs") or []
    top_songs = [
        await format_song(s, lyrics_func)
        for s in top_songs_raw
        if isinstance(s, dict)
    ]

    # topAlbums lives under data["topAlbums"]["albums"] (not ["data"])
    top_albums_raw = (data.get("topAlbums") or {}).get("albums") or []
    top_albums = [_format_album_brief(a) for a in top_albums_raw if isinstance(a, dict)]

    # singles (may not exist on all responses)
    singles_raw = (data.get("singles") or {}).get("songs") or []
    singles = [
        await format_song(s, lyrics_func)
        for s in singles_raw
        if isinstance(s, dict)
    ]

    # Similar artists
    similar_raw = (data.get("similarArtists") or {}).get("artists") or []
    similar_artists = [_format_similar_artist(a) for a in similar_raw if isinstance(a, dict)]

    return {
        "id": data.get("artistId") or data.get("id"),
        "name": clean(data.get("name")),
        "image": image,
        "follower_count": data.get("follower_count"),
        "fan_count": data.get("fan_count"),
        "is_verified": data.get("isVerified"),
        "dominant_language": data.get("dominantLanguage"),
        "dominant_type": data.get("dominantType"),
        "bio": bio_text,
        "dob": data.get("dob"),
        "fb": data.get("fb"),
        "twitter": data.get("twitter"),
        "wiki": data.get("wiki"),
        "available_languages": data.get("availableLanguages") or [],
        "top_songs": top_songs,
        "top_albums": top_albums,
        "singles": singles,
        "similar_artists": similar_artists,
    }


def _format_album_brief(data: dict) -> dict:
    return {
        "id": data.get("id") or data.get("albumid"),
        "name": clean(data.get("name") or data.get("title")),
        "year": data.get("year"),
        "image": (data.get("image") or "").replace("150x150", "500x500"),
        "primary_artists": clean(data.get("primary_artists") or ""),
        "language": data.get("language"),
        "song_count": data.get("song_count"),
    }


def _format_similar_artist(data: dict) -> dict:
    return {
        "id": data.get("id"),
        "name": clean(data.get("name")),
        "image": (data.get("image") or "").replace("150x150", "500x500"),
        "dominant_type": data.get("dominantType") or data.get("dominant_type"),
        "dominant_language": data.get("dominantLanguage") or data.get("dominant_language"),
    }
