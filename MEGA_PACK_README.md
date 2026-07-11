# SaavnAPI Mega Feature Pack

25 new features across 6 packs, added to your existing `JioSaavn` package.

## Installation

1. Copy the `JioSaavn/Modules/`, `JioSaavn/Analysis/`, `JioSaavn/Servers/`,
   and `JioSaavn/Utils/` files into your existing package tree.
2. Append the contents of `JioSaavn/__init___patch.py` to your existing
   `JioSaavn/__init__.py`.
3. Install optional deps as you need them:

```bash
pip install mutagen         # ID3 tagging + embedded lyrics
pip install aioresponses    # tests
pip install mcp             # MCP server
pip install strawberry-graphql[fastapi] uvicorn   # GraphQL
pip install websockets      # WebSocket broadcaster
```

## Feature index

### 🤖 AI Pack
- `analyze_playlist(songs)` — BPM-adjacent stats, top artists, decade breakdown, dominant language
- `find_duplicates(songs, threshold=0.9)` — fuzzy duplicate detection
- `infer_mood(song)` — mood label from title + lyrics
- `recommend_from_history(client, history)` — history-based recommender
- `search_by_lyrics(client, snippet)` — find songs by lyric fragment

### 🔄 Sync Pack
- `sync_spotify_playlist(client, url)` — Spotify → JioSaavn matcher
- `sync_youtube_playlist(client, url)` — YouTube → JioSaavn matcher
- `backup_library(data, path)` — JSON or SQLite backup
- `restore_library(path)` — restore from backup

### ⬇️ Downloader Pro
- `DownloadManager` — persistent SQLite queue, pause/resume, concurrency
- `download_with_lyrics(client, song_id, path)` — embeds synced lyrics into MP3 (USLT frame)

### 🔍 Discovery Pack
- `daily_mix(client, seeds)` — deterministic daily rotating mix
- `time_machine(client, year)` — top songs from a specific year
- `regional_charts(client, language)` — charts filtered by language
- `artist_radio(client, artist_id)` — infinite artist-based station
- `SmartQueue` — auto-refilling infinite queue

### 🛠️ Dev Tools Pack
- `python -m JioSaavn.Servers.MCP` — Model Context Protocol server (Claude / ChatGPT / Cursor)
- `JioSaavn.Servers.GraphQL.build_app()` — GraphQL layer over REST
- `python -m JioSaavn.Servers.WebSocket` — WS broadcaster for now-playing
- `WebhookNotifier` — fire webhooks on new releases from followed artists

### 👥 Social / Metadata
- `get_song_credits(client, song_id)` — composer/lyricist/producer
- `get_release_calendar(client)` — upcoming/new releases
- `compare_artists(client, a, b)` — side-by-side artist stats

### 🔎 Advanced Search
- `fuzzy_search(client, query)` — typo-tolerant
- `search_filters(songs, ...)` — filter by year/language/duration/explicit

### 🎛️ Playback
- `crossfade_plan(current, next)` — fade timing metadata for players

## Environment variables

```bash
export SPOTIFY_CLIENT_ID=...
export SPOTIFY_CLIENT_SECRET=...
export YOUTUBE_API_KEY=...
```

## Notes

- All async modules are `aiohttp`-native.
- The download manager and webhook notifier persist state to disk between runs.
- MCP / GraphQL / WebSocket servers use optional deps loaded lazily.
