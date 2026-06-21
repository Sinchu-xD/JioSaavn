# 🎧 SaavnAPI

> ⚡ Fast, Async JioSaavn API Wrapper for Python

A powerful, fully-asynchronous Python library for JioSaavn — search songs, fetch artist profiles, get trending tracks, stream URLs, lyrics, albums, playlists, charts, and more.

---

## 🚀 Features

- ⚡ **Fully Async** — aiohttp based, built for speed
- 🔍 **Full Search** — songs, albums, artists, playlists with pagination
- 👤 **Artist Profiles** — bio, top songs, albums, singles, similar artists, social links
- 🔥 **Trending** — live trending songs with language filter
- 📊 **Charts & Playlists** — top charts, featured editorial playlists
- 🆕 **New Releases** — latest album releases
- 🎯 **Suggestions** — song recommendations engine
- 🎵 **Stream URLs** — decrypted 320 kbps direct MP4 links
- 📝 **Lyrics** — full plain-text lyrics
- 💿 **Albums & Playlists** — complete track listings
- ⚡ **Session Client** — reusable aiohttp session for batch requests
- 🧠 **Clean & Modular** — consistent, normalised response dicts

---

## 📦 Installation

```bash
pip install SaavnAPI
```

**Requires:** Python 3.10+

---

## ⚡ Quick Start

```python
import asyncio
from JioSaavn import (
    search, get_song, get_lyrics,
    get_artist, get_trending,
    get_charts, get_suggestions,
    JioSaavnClient,
)

async def main():
    # Search songs
    songs = await search("Arijit Singh", limit=5)
    for s in songs:
        print(s["song"], "—", s["primary_artists"])

    # Artist profile (NEW)
    artist = await get_artist("arijit-singh")
    print(artist["name"], "followers:", artist["follower_count"])
    for t in artist["top_songs"][:3]:
        print("  ▶", t["song"])

    # Trending (NEW)
    trending = await get_trending(language="hindi", limit=10)
    for t in trending:
        print(t["song"], "—", t["views"], "plays")

    # Suggestions (NEW)
    recs = await get_suggestions("4ZSL1xJk", limit=5)

    # Batch requests with one shared session
    async with JioSaavnClient() as client:
        charts   = await get_charts(client=client)
        trending = await get_trending(limit=20, client=client)

asyncio.run(main())
```

---

## 📚 All Functions

| Function | Description |
|---|---|
| `search(query)` | Search songs by keyword |
| `search_songs(query)` | Search songs with pagination |
| `search_albums(query)` | Search albums |
| `search_artists(query)` | Search artists |
| `search_playlists(query)` | Search playlists |
| `get_song(song_id)` | Song details + 320kbps stream URL |
| `get_lyrics(song_id)` | Plain-text lyrics |
| `get_suggestions(song_id)` | ✨ Song recommendations |
| `get_artist(artist_id)` | ✨ Full artist profile |
| `get_artist_top_songs(artist_id)` | ✨ Paginated artist songs |
| `get_artist_top_albums(artist_id)` | ✨ Paginated artist albums |
| `get_album(album_id)` | Album + track listing |
| `get_playlist(list_id)` | Playlist + all songs |
| `get_trending()` | ✨ Trending songs by language |
| `get_new_releases()` | ✨ New album releases |
| `get_charts()` | ✨ Top chart playlists |
| `get_featured_playlists()` | ✨ Editorial playlists |

---

## 👤 Artist Profile (New)

```python
from JioSaavn import get_artist

# By URL slug
artist = await get_artist("arijit-singh")

# By numeric ID
artist = await get_artist("459320")

print(artist["name"])
print(f"Followers: {artist['follower_count']}")
print(f"Bio: {artist['bio'][:100]}")

for song in artist["top_songs"][:5]:
    print(f"  ▶ {song['song']} ({song['year']})")

for album in artist["top_albums"][:3]:
    print(f"  💿 {album['name']} ({album['year']})")

for similar in artist["similar_artists"][:3]:
    print(f"  👤 {similar['name']}")
```

---

## 🔥 Trending (New)

```python
from JioSaavn import get_trending

# All languages
trending = await get_trending(limit=20)

# Filter by language
trending = await get_trending(language=["hindi", "punjabi"], limit=10)

for t in trending:
    print(t["song"], "—", t["views"], "plays")
```

---

## 📊 Charts & Playlists (New)

```python
from JioSaavn import get_charts, get_featured_playlists, get_playlist

# Top charts
charts = await get_charts()
for c in charts:
    print(c["name"], "—", c["song_count"], "songs")

# Get songs from a chart
songs = await get_playlist(charts[0]["id"])

# Featured/editorial playlists
featured = await get_featured_playlists(language="hindi", limit=10)
```

---

## 🎯 Song Suggestions (New)

```python
from JioSaavn import get_suggestions

recs = await get_suggestions("4ZSL1xJk", limit=5)
for r in recs:
    print(r["song"], "—", r["primary_artists"])
```

---

## ⚠️ Disclaimer

This is an unofficial API wrapper. JioSaavn may change their internal API at any time. Not affiliated with JioSaavn / Saavn Media Ltd.

---

## 📜 License

MIT License

---

## 👑 Author

Made with ❤️ by **Abhi Singh**  
PyPI: [pypi.org/project/SaavnAPI](https://pypi.org/project/SaavnAPI/)
