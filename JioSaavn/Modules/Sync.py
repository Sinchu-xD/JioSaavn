"""Cross-platform playlist sync — Spotify & YouTube → JioSaavn.

Requires:
- Spotify: SPOTIFY_CLIENT_ID + SPOTIFY_CLIENT_SECRET env vars (client-credentials flow).
- YouTube: YOUTUBE_API_KEY env var (Data API v3).
"""
from __future__ import annotations
import os
import re
from typing import Any
import aiohttp


SPOTIFY_PLAYLIST_RE = re.compile(r"(?:playlist[/:])([A-Za-z0-9]+)")
YT_PLAYLIST_RE = re.compile(r"[?&]list=([A-Za-z0-9_-]+)")


async def _spotify_token(session: aiohttp.ClientSession) -> str:
    cid = os.environ.get("SPOTIFY_CLIENT_ID")
    secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    if not cid or not secret:
        raise RuntimeError("SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET not set")
    async with session.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=aiohttp.BasicAuth(cid, secret),
    ) as r:
        r.raise_for_status()
        return (await r.json())["access_token"]


async def sync_spotify_playlist(client: Any, url_or_id: str, limit: int = 100) -> dict:
    """Convert a Spotify playlist to matched JioSaavn songs."""
    m = SPOTIFY_PLAYLIST_RE.search(url_or_id)
    pid = m.group(1) if m else url_or_id
    matched, unmatched = [], []
    async with aiohttp.ClientSession() as session:
        token = await _spotify_token(session)
        async with session.get(
            f"https://api.spotify.com/v1/playlists/{pid}/tracks?limit={limit}",
            headers={"Authorization": f"Bearer {token}"},
        ) as r:
            r.raise_for_status()
            items = (await r.json()).get("items", [])
    for it in items:
        tr = (it or {}).get("track") or {}
        name = tr.get("name")
        artists = ", ".join(a["name"] for a in tr.get("artists", []))
        if not name:
            continue
        query = f"{name} {artists}".strip()
        try:
            results = await client.search_songs(query, limit=1)
            hit = (results or [None])[0]
        except Exception:
            hit = None
        (matched if hit else unmatched).append({"query": query, "match": hit})
    return {"matched": matched, "unmatched": unmatched, "match_rate": len(matched) / max(len(matched) + len(unmatched), 1)}


async def sync_youtube_playlist(client: Any, url_or_id: str, limit: int = 50) -> dict:
    """Convert a YouTube playlist to matched JioSaavn songs."""
    key = os.environ.get("YOUTUBE_API_KEY")
    if not key:
        raise RuntimeError("YOUTUBE_API_KEY not set")
    m = YT_PLAYLIST_RE.search(url_or_id)
    plid = m.group(1) if m else url_or_id
    matched, unmatched = [], []
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://www.googleapis.com/youtube/v3/playlistItems",
            params={"part": "snippet", "playlistId": plid, "maxResults": min(limit, 50), "key": key},
        ) as r:
            r.raise_for_status()
            items = (await r.json()).get("items", [])
    for it in items:
        title = (it.get("snippet") or {}).get("title") or ""
        # Strip common YT junk
        query = re.sub(r"\(.*?official.*?\)|\[.*?\]|official video|lyrics", "", title, flags=re.I).strip()
        try:
            results = await client.search_songs(query, limit=1)
            hit = (results or [None])[0]
        except Exception:
            hit = None
        (matched if hit else unmatched).append({"query": query, "match": hit})
    return {"matched": matched, "unmatched": unmatched, "match_rate": len(matched) / max(len(matched) + len(unmatched), 1)}
