# 🎧 SaavnKit — The Complete JioSaavn Async Toolkit

> ⚡ **v2026.7.11** — Fast, fully-async Python library for JioSaavn with 70+ features: core APIs, downloads, AI analysis, smart discovery, sync with Spotify/YouTube, MCP/GraphQL/WebSocket servers, and more.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)]()
[![Async](https://img.shields.io/badge/async-aiohttp-green.svg)]()
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)]()

---

## 📦 Installation

```bash
# Base install
pip install -e .

# With extras
pip install -e ".[download]"   # ID3 tagging (mutagen)
pip install -e ".[servers]"    # MCP, GraphQL, WebSocket
pip install -e ".[sync]"       # Spotify/YouTube sync
pip install -e ".[all]"        # everything
pip install -e ".[dev]"        # dev/test tools
```

Docs: open `index.html` in your browser, or visit **saavn-api.netlify.app**.

---

## 🚀 Quick Start

```python
import asyncio
from JioSaavn import JioSaavnClient

async def main():
    async with JioSaavnClient() as client:
        results = await client.search_songs("Kesariya", limit=5)
        for s in results:
            print(s["name"], "—", s["primaryArtists"])

asyncio.run(main())
```

---

## 🧭 Feature Map (70+)

### 1. Core Music APIs (26)
| Category      | Functions |
|---------------|-----------|
| **Song**      | `get_song`, `get_songs`, `get_lyrics`, `get_suggestions` |
| **Album**     | `get_album`, `get_album_by_url` |
| **Artist**    | `get_artist`, `get_artist_top_songs`, `get_artist_top_albums` |
| **Playlist**  | `get_playlist`, `get_playlist_by_url` |
| **Search**    | `search`, `search_songs`, `search_albums`, `search_artists`, `search_playlists`, `search_all` |
| **Discovery** | `get_trending`, `get_new_releases`, `get_top_searches`, `get_charts`, `get_featured_playlists`, `get_modules`, `get_radio` |
| **Resolve**   | `get_song_by_url` |

### 2. Download Helper Pro
- `download_with_lyrics(client, song_id, path, bitrate=320)` — 320kbps + ID3 tags + embedded USLT lyrics
- `DownloadManager` — persistent SQLite-backed queue with retry, resume, and progress

```python
from JioSaavn.Modules.DownloadPro import DownloadManager, download_with_lyrics
await download_with_lyrics(client, "song_id", "./out.mp3")
```

### 3. Language / Mood / Genre Browse
Supported: 16 languages · 12 moods · 14 genres (see `JioSaavn/Modules/Browse.py`-equivalent via search filters).

### 4. AI Analysis
- `analyze_playlist(songs)` — stats, top artists, avg duration, language mix
- `find_duplicates(songs, threshold=0.9)` — fuzzy duplicate finder
- `infer_mood(song)` — mood classification
- `recommend_from_history(client, history)` — personalized recs
- `similar_songs_deep(client, seed_id, hops=2)` — graph-walk similarity

### 5. Smart Playback
- `SmartQueue` — infinite auto-refill queue based on current track
- `crossfade_plan(current, next_, fade_seconds=6)` — crossfade timing metadata

### 6. Sync & Backup
- `sync_spotify_playlist(client, url_or_id)` — match Spotify → JioSaavn
- `sync_youtube_playlist(client, url_or_id)` — match YouTube → JioSaavn
- `backup_library(data, path, format="json"|"sqlite")` / `restore_library(path)`

### 7. Advanced Search
- `fuzzy_search(client, query, min_score=0.5)` — typo-tolerant
- `search_by_lyrics(client, snippet)` — find songs by lyric fragments
- `search_filters(...)` — combine language/year/duration constraints

### 8. Discovery Pack
- `daily_mix(client, seed_songs, size=30)`
- `time_machine(client, year, limit=30)` — by release year
- `regional_charts(client, language)`
- `artist_radio(client, artist_id, size=30)`

### 9. Social / Metadata
- `get_song_credits(client, song_id)` — full credits
- `get_release_calendar(client, days_back=30)`
- `compare_artists(client, id_a, id_b)`

### 10. Webhooks
- `WebhookNotifier` — push new releases / chart changes to a URL with HMAC signing

### 11. Dev Servers
| Server      | Module                       | Purpose |
|-------------|------------------------------|---------|
| **MCP**     | `JioSaavn.Servers.MCP`       | Model Context Protocol server for LLMs |
| **GraphQL** | `JioSaavn.Servers.GraphQL`   | Strawberry-based GraphQL API |
| **WebSocket** | `JioSaavn.Servers.WebSocket` | Now-playing hub for real-time apps |

### 12. Infrastructure
- Async LRU cache with TTL (`Utils/Cache`)
- Token-bucket rate limiter (`Utils/RateLimit`)
- Typed exception hierarchy (`Core/Errors`)
- Exponential backoff + auto-retry HTTP layer
- Full type hints (`py.typed`) + `TypedDict` models
- GitHub Actions CI (tests + lint)

---

## 🧪 Testing

Run the interactive tester covering **all 70+ features**:

```bash
python Testing.py             # run all suites
python Testing.py --suite core        # core APIs only
python Testing.py --suite mega        # AI / discovery / smart queue
python Testing.py --suite servers     # MCP / GraphQL / WebSocket smoke
python Testing.py --list              # show all available tests
```

Last full run: **45 / 47 passing** (2 geo-blocked in test region).

---

## 📚 Examples

### Playlist analysis
```python
from JioSaavn.Analysis.Playlist import analyze_playlist, find_duplicates
pl = await client.get_playlist("110858205")
stats = analyze_playlist(pl["songs"])
dupes = find_duplicates(pl["songs"])
```

### Daily mix
```python
from JioSaavn.Modules.Discovery import daily_mix
mix = await daily_mix(client, seed_songs=["5WXAlMNt", "9BjJPi9d"], size=30)
```

### Spotify → JioSaavn
```python
from JioSaavn.Modules.Sync import sync_spotify_playlist
result = await sync_spotify_playlist(client, "https://open.spotify.com/playlist/...")
```

### MCP server (for Claude / LLMs)
```bash
python -m JioSaavn.Servers.MCP
```

---

## 📜 License

MIT — free for personal & educational use. Not affiliated with JioSaavn.

## 🙏 Credits

Maintained by the SaavnKit community. PRs welcome — see `CONTRIBUTING.md`.
