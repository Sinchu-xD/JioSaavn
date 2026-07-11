from __future__ import annotations

from ..Utils.Crypto import decrypt
from ..Utils.Text import clean


async def format_song(data: dict, lyrics_func=None) -> dict:
    more: dict = data.get("more_info") or {}

    duration_raw = more.get("duration")
    duration: str | None = None
    if duration_raw:
        try:
            secs = int(duration_raw)
            duration = f"{secs // 60}:{secs % 60:02d}"
        except (ValueError, TypeError):
            duration = None

    image = data.get("image") or ""
    if image:
        image = image.replace("150x150", "500x500")

    artists = more.get("artistMap") or {}
    primary = artists.get("primary_artists") or []
    primary_artists = ", ".join(
        a.get("name", "") for a in primary if isinstance(a, dict)
    )

    featured = artists.get("featured_artists") or []
    featured_artists = ", ".join(
        a.get("name", "") for a in featured if isinstance(a, dict)
    )

    all_artists = artists.get("artists") or []
    all_artist_names = ", ".join(
        a.get("name", "") for a in all_artists if isinstance(a, dict)
    )

    enc = more.get("encrypted_media_url")
    media_url: str | None = None
    if enc:
        media_url = decrypt(enc)
        if media_url and more.get("320kbps") != "true":
            media_url = media_url.replace("_320.mp4", "_160.mp4")

    views = data.get("play_count") or more.get("play_count") or more.get("view_count")

    lyrics: str | None = None
    if lyrics_func and more.get("has_lyrics") == "true":
        song_id = data.get("id")
        if song_id:
            lyrics = await lyrics_func(song_id)

    release_date = more.get("release_date") or more.get("releaseDate")

    return {
        "id": data.get("id"),
        "song": clean(data.get("title")),
        "album": clean(more.get("album")),
        "album_id": more.get("album_id"),
        "music": clean(more.get("music")),
        "music_id": more.get("music_id"),
        "primary_artists": primary_artists,
        "featured_artists": featured_artists,
        "all_artists": all_artist_names,
        "image": image,
        "duration": duration,
        "views": views,
        "media_url": media_url,
        "lyrics": lyrics,
        "language": data.get("language"),
        "year": data.get("year"),
        "release_date": release_date,
        "has_lyrics": more.get("has_lyrics") == "true",
        "label": more.get("label"),
        "explicit": more.get("explicit_content") == "1",
        "copyright": more.get("copyright_text"),
    }
