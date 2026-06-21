from __future__ import annotations

from ..Utils.Text import clean
from .Song import format_song


async def format_album(data: dict, lyrics_func=None) -> dict:
    songs_raw = data.get("songs") or []
    songs = [await format_song(s, lyrics_func) for s in songs_raw if isinstance(s, dict)]

    return {
        "id": data.get("id") or data.get("albumid"),
        "name": clean(data.get("name") or data.get("title")),
        "title": clean(data.get("title") or data.get("name")),
        "primary_artists": clean(data.get("primary_artists")),
        "image": (data.get("image") or "").replace("150x150", "500x500"),
        "year": data.get("year"),
        "release_date": data.get("release_date"),
        "language": data.get("language"),
        "label": data.get("label_name") or data.get("label"),
        "copyright": data.get("copyright_text"),
        "song_count": data.get("song_count") or len(songs),
        "songs": songs,
    }
