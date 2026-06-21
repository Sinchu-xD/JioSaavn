from __future__ import annotations

from ..Utils.Text import clean
from .Song import format_song


async def format_playlist(data: dict, lyrics_func=None) -> dict:
    songs_raw = data.get("songs") or []
    songs = [await format_song(s, lyrics_func) for s in songs_raw if isinstance(s, dict)]

    return {
        "id": data.get("id") or data.get("listid"),
        "listname": clean(data.get("listname") or data.get("title")),
        "firstname": clean(data.get("firstname")),
        "lastname": clean(data.get("lastname")),
        "uid": data.get("uid"),
        "follower_count": data.get("follower_count"),
        "fan_count": data.get("fan_count"),
        "song_count": data.get("song_count") or len(songs),
        "image": (data.get("image") or "").replace("150x150", "500x500"),
        "language": data.get("language"),
        "play_count": data.get("play_count"),
        "songs": songs,
    }
