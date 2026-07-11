"""Curated language / mood / genre browse for JioSaavn."""
from __future__ import annotations

from typing import Any

LANGUAGES: list[str] = [
    "hindi", "english", "punjabi", "tamil", "telugu", "marathi", "gujarati",
    "bengali", "kannada", "bhojpuri", "malayalam", "urdu", "haryanvi",
    "rajasthani", "odia", "assamese",
]

MOODS: list[str] = [
    "romantic", "happy", "sad", "party", "chill", "workout", "focus",
    "sleep", "devotional", "monsoon", "travel", "nostalgic",
]

GENRES: list[str] = [
    "pop", "rock", "hip hop", "classical", "ghazal", "bhajan", "sufi",
    "folk", "indie", "edm", "jazz", "reggae", "instrumental", "soundtrack",
]


async def browse_language(client: Any, language: str, limit: int = 20) -> list[dict]:
    """Top songs curated by language."""
    language = language.lower().strip()
    if language not in LANGUAGES:
        raise ValueError(f"Unknown language {language!r}. Supported: {LANGUAGES}")
    return await client.search_songs(f"top {language} songs", limit=limit)


async def browse_mood(client: Any, mood: str, limit: int = 20) -> list[dict]:
    """Songs for a given mood."""
    mood = mood.lower().strip()
    if mood not in MOODS:
        raise ValueError(f"Unknown mood {mood!r}. Supported: {MOODS}")
    return await client.search_songs(f"{mood} songs", limit=limit)


async def browse_genre(client: Any, genre: str, limit: int = 20) -> list[dict]:
    """Songs for a given genre."""
    genre = genre.lower().strip()
    if genre not in GENRES:
        raise ValueError(f"Unknown genre {genre!r}. Supported: {GENRES}")
    return await client.search_songs(f"{genre} music", limit=limit)


def list_categories() -> dict[str, list[str]]:
    return {"languages": LANGUAGES, "moods": MOODS, "genres": GENRES}


__all__ = [
    "LANGUAGES", "MOODS", "GENRES",
    "browse_language", "browse_mood", "browse_genre", "list_categories",
]
