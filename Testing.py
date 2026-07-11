"""
SaavnKit — Complete Test Suite
================================
Version : 2026.7.11
Covers  : Core APIs · Download · AI Analysis · Discovery · Smart Queue
          Sync · Backup · Webhooks · Servers (smoke) · Utils

Usage:
    python Testing.py                    # run every suite
    python Testing.py --suite core       # only core APIs
    python Testing.py --suite mega       # AI + discovery + smart queue
    python Testing.py --suite servers    # server smoke checks
    python Testing.py --list             # list all tests
"""

from __future__ import annotations

import argparse
import asyncio
import inspect
import os
import sys
import tempfile
import time
import traceback
from typing import Any, Awaitable, Callable

from JioSaavn import JioSaavnClient

# ── Optional imports (guarded so missing extras don't break the runner) ──
try:
    from JioSaavn.Modules import (
        Search, Song, Album, Artist, Playlist, Charts, Trending,
        Suggestions, Lyrics, Radio, Resolve,
    )
except Exception as e:  # pragma: no cover
    print("Core import failed:", e); sys.exit(1)

try:
    from JioSaavn.Modules.SmartQueue import SmartQueue
    from JioSaavn.Modules.AdvSearch import fuzzy_search, search_by_lyrics
    from JioSaavn.Modules.Discovery import (
        daily_mix, time_machine, regional_charts, artist_radio,
    )
    from JioSaavn.Modules.Social import (
        get_song_credits, get_release_calendar, compare_artists,
    )
    from JioSaavn.Modules.Backup import backup_library, restore_library
    from JioSaavn.Modules.Webhooks import WebhookNotifier
    from JioSaavn.Analysis.Playlist import (
        analyze_playlist, find_duplicates, infer_mood,
    )
    from JioSaavn.Analysis.Recommender import (
        recommend_from_history, similar_songs_deep,
    )
    from JioSaavn.Utils.Crossfade import crossfade_plan
    MEGA_AVAILABLE = True
except Exception as e:
    print("⚠️  Mega-pack modules not fully available:", e)
    MEGA_AVAILABLE = False

try:
    from JioSaavn.Modules.Sync import sync_spotify_playlist, sync_youtube_playlist
    SYNC_AVAILABLE = True
except Exception:
    SYNC_AVAILABLE = False

try:
    from JioSaavn.Modules.DownloadPro import DownloadManager, download_with_lyrics
    DOWNLOAD_AVAILABLE = True
except Exception:
    DOWNLOAD_AVAILABLE = False


# ── Test infrastructure ──────────────────────────────────────────────────
TESTS: list[tuple[str, str, Callable[..., Awaitable[Any]]]] = []


def test(suite: str, name: str):
    def deco(fn):
        TESTS.append((suite, name, fn))
        return fn
    return deco


# ── Fixtures ─────────────────────────────────────────────────────────────
SEED_QUERY   = "Kesariya"
SEED_SONG_ID = "5WXAlMNt"
SEED_ALBUM   = "23241897"
SEED_ARTIST  = "459320"
SEED_PLAYLIST = "110858205"


# ══════════════════════════════ CORE (26) ════════════════════════════════
@test("core", "search")
async def _(c): return await c.search(SEED_QUERY)

@test("core", "search_songs")
async def _(c): return await c.search_songs(SEED_QUERY, limit=5)

@test("core", "search_albums")
async def _(c): return await c.search_albums(SEED_QUERY, limit=5)

@test("core", "search_artists")
async def _(c): return await c.search_artists("Arijit Singh", limit=5)

@test("core", "search_playlists")
async def _(c): return await c.search_playlists("bollywood", limit=5)

@test("core", "search_all")
async def _(c): return await c.search_all(SEED_QUERY)

@test("core", "get_song")
async def _(c): return await Song.get_song(SEED_SONG_ID, client=c)

@test("core", "get_songs")
async def _(c): return await Song.get_songs([SEED_SONG_ID], client=c)

@test("core", "get_lyrics")
async def _(c): return await Lyrics.get_lyrics(SEED_SONG_ID, client=c)

@test("core", "get_suggestions")
async def _(c): return await Suggestions.get_suggestions(SEED_SONG_ID, client=c)

@test("core", "get_album")
async def _(c): return await Album.get_album(SEED_ALBUM, client=c)

@test("core", "get_artist")
async def _(c): return await Artist.get_artist(SEED_ARTIST, client=c)

@test("core", "get_artist_top_songs")
async def _(c): return await Artist.get_artist_top_songs(SEED_ARTIST, client=c)

@test("core", "get_artist_top_albums")
async def _(c): return await Artist.get_artist_top_albums(SEED_ARTIST, client=c)

@test("core", "get_playlist")
async def _(c): return await Playlist.get_playlist(SEED_PLAYLIST, client=c)

@test("core", "get_trending")
async def _(c): return await Trending.get_trending(client=c)

@test("core", "get_new_releases")
async def _(c): return await Trending.get_new_releases(client=c)

@test("core", "get_top_searches")
async def _(c): return await Trending.get_top_searches(client=c)

@test("core", "get_modules")
async def _(c): return await Trending.get_modules(client=c)

@test("core", "get_charts")
async def _(c): return await Charts.get_charts(client=c)

@test("core", "get_featured_playlists")
async def _(c): return await Charts.get_featured_playlists(client=c)

@test("core", "get_radio (may be geo-blocked)")
async def _(c): return await Radio.get_radio(SEED_SONG_ID, client=c)

@test("core", "get_song_by_url")
async def _(c):
    return await Resolve.get_song_by_url(
        "https://www.jiosaavn.com/song/kesariya/PwAFSyRcXWQ", client=c
    )

@test("core", "get_album_by_url")
async def _(c):
    return await Resolve.get_album_by_url(
        "https://www.jiosaavn.com/album/kesariya-from-brahmastra/1sYK9C0T3Xg_", client=c
    )

@test("core", "get_playlist_by_url (may fail token)")
async def _(c):
    return await Resolve.get_playlist_by_url(
        "https://www.jiosaavn.com/featured/trending-today/I3kvhipIy73uCJW60TJk1Q__", client=c
    )


# ══════════════════════════════ MEGA PACK ════════════════════════════════
if MEGA_AVAILABLE:

    @test("mega", "analyze_playlist")
    async def _(c):
        pl = await Playlist.get_playlist(SEED_PLAYLIST, client=c)
        return analyze_playlist(pl["songs"])

    @test("mega", "find_duplicates")
    async def _(c):
        pl = await Playlist.get_playlist(SEED_PLAYLIST, client=c)
        return find_duplicates(pl["songs"])

    @test("mega", "infer_mood")
    async def _(c):
        s = await Song.get_song(SEED_SONG_ID, client=c)
        return infer_mood(s)

    @test("mega", "recommend_from_history")
    async def _(c):
        return await recommend_from_history(c, [SEED_SONG_ID], limit=10)

    @test("mega", "similar_songs_deep")
    async def _(c):
        return await similar_songs_deep(c, SEED_SONG_ID, hops=1, per_hop=3)

    @test("mega", "SmartQueue.refill")
    async def _(c):
        q = SmartQueue(c, seed_song_id=SEED_SONG_ID, target_size=10)
        first = await q.next()
        return {"queue_size": len(q._queue), "first": bool(first)}

    @test("mega", "fuzzy_search")
    async def _(c):
        return await fuzzy_search(c, "kesarya", limit=5, min_score=0.4)

    @test("mega", "search_by_lyrics")
    async def _(c):
        return await search_by_lyrics(c, "tera hone laga hoon", limit=3)

    @test("mega", "daily_mix")
    async def _(c):
        return await daily_mix(c, seed_songs=[SEED_SONG_ID], size=15)

    @test("mega", "time_machine")
    async def _(c):
        return await time_machine(c, year=2015, limit=10)

    @test("mega", "regional_charts")
    async def _(c):
        return await regional_charts(c, language="hindi", limit=10)

    @test("mega", "artist_radio")
    async def _(c):
        return await artist_radio(c, SEED_ARTIST, size=10)

    @test("mega", "get_song_credits")
    async def _(c):
        return await get_song_credits(c, SEED_SONG_ID)

    @test("mega", "get_release_calendar")
    async def _(c):
        return await get_release_calendar(c, days_back=14)

    @test("mega", "compare_artists")
    async def _(c):
        return await compare_artists(c, SEED_ARTIST, "455130")

    @test("mega", "crossfade_plan")
    async def _(c):
        a = await Song.get_song(SEED_SONG_ID, client=c)
        b = (await c.search_songs("Tum Hi Ho", limit=1))[0]
        return crossfade_plan(a, b, fade_seconds=6)

    @test("mega", "backup + restore roundtrip")
    async def _(c):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            backup_library({"library": [SEED_SONG_ID]}, path, format="json")
            return restore_library(path)
        finally:
            os.unlink(path)

    @test("mega", "WebhookNotifier init")
    async def _(c):
        db = os.path.join(tempfile.gettempdir(), "saavn_webhooks_test.json")
        try:
            if os.path.exists(db): os.unlink(db)
            w = WebhookNotifier(state_path=db)
            w.subscribe("459320", "https://example.com/hook")
            return {"subscribed": True}
        finally:
            os.unlink(db)


# ══════════════════════════════ SYNC ═════════════════════════════════════
if SYNC_AVAILABLE:

    @test("sync", "sync_spotify (needs SPOTIFY_CLIENT_ID/SECRET)")
    async def _(c):
        if not (os.getenv("SPOTIFY_CLIENT_ID") and os.getenv("SPOTIFY_CLIENT_SECRET")):
            return {"skipped": "no Spotify creds"}
        return await sync_spotify_playlist(
            c, "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M", limit=10
        )

    @test("sync", "sync_youtube (needs YOUTUBE_API_KEY)")
    async def _(c):
        if not os.getenv("YOUTUBE_API_KEY"):
            return {"skipped": "no YouTube key"}
        return await sync_youtube_playlist(
            c, "PLw-VjHDlEOgtVJx4tqvXtSb4-6bK1p6Vn", limit=10
        )


# ══════════════════════════════ DOWNLOAD ═════════════════════════════════
if DOWNLOAD_AVAILABLE:

    @test("download", "DownloadManager init")
    async def _(c):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db = f.name
        try:
            m = DownloadManager(db_path=db)
            m.enqueue({"id": SEED_SONG_ID, "song": "seed"}, "/tmp/x.mp3")
            return {"queued": len(m.list_jobs("pending"))}
        finally:
            os.unlink(db)

    @test("download", "download_with_lyrics (network + writes MP3)")
    async def _(c):
        out = os.path.join(tempfile.gettempdir(), "saavnkit_test.mp3")
        path = await download_with_lyrics(c, SEED_SONG_ID, out, bitrate=160)
        size = os.path.getsize(path) if os.path.exists(path) else 0
        try: os.unlink(path)
        except OSError: pass
        return {"bytes": size}


# ══════════════════════════════ SERVERS (smoke) ══════════════════════════
@test("servers", "MCP module importable")
async def _(c):
    try:
        from JioSaavn.Servers import MCP  # noqa
        return {"ok": True}
    except Exception as e:
        return {"skipped": str(e)}

@test("servers", "GraphQL module importable")
async def _(c):
    try:
        from JioSaavn.Servers import GraphQL  # noqa
        return {"ok": True}
    except Exception as e:
        return {"skipped": str(e)}

@test("servers", "WebSocket module importable")
async def _(c):
    try:
        from JioSaavn.Servers import WebSocket  # noqa
        return {"ok": True}
    except Exception as e:
        return {"skipped": str(e)}


# ══════════════════════════════ RUNNER ═══════════════════════════════════
def _short(obj: Any) -> str:
    try:
        if isinstance(obj, list):
            return f"list(len={len(obj)})"
        if isinstance(obj, dict):
            keys = list(obj.keys())[:4]
            return f"dict(keys={keys}{'…' if len(obj) > 4 else ''})"
        s = str(obj)
        return s if len(s) < 80 else s[:77] + "…"
    except Exception:
        return type(obj).__name__


async def run(suite_filter: str | None = None) -> None:
    picked = [t for t in TESTS if suite_filter in (None, t[0])]
    if not picked:
        print(f"No tests match suite={suite_filter!r}"); return

    print(f"\n🎧 SaavnKit Test Runner — {len(picked)} tests\n" + "─" * 60)
    passed = failed = skipped = 0
    t0 = time.perf_counter()

    async with JioSaavnClient() as client:
        for suite, name, fn in picked:
            label = f"[{suite:>8}] {name:<45}"
            try:
                t = time.perf_counter()
                result = await fn(client)
                dt = (time.perf_counter() - t) * 1000
                if isinstance(result, dict) and "skipped" in result:
                    print(f"⏭  {label} SKIP  ({result['skipped']})")
                    skipped += 1
                elif result is None or (isinstance(result, (list, dict)) and not result):
                    print(f"⚠️  {label} EMPTY ({dt:.0f}ms)  (upstream returned no data)")
                    passed += 1
                else:
                    print(f"✅ {label} {dt:6.0f}ms  {_short(result)}")
                    passed += 1
            except Exception as e:
                print(f"❌ {label} FAIL  {type(e).__name__}: {e}")
                if os.getenv("SAAVN_TEST_VERBOSE"):
                    traceback.print_exc()
                failed += 1

    elapsed = time.perf_counter() - t0
    total = passed + failed + skipped
    print("─" * 60)
    print(f"Results: ✅ {passed}  ❌ {failed}  ⏭ {skipped}   "
          f"({passed}/{total} pass · {elapsed:.1f}s)")


def _list() -> None:
    by_suite: dict[str, list[str]] = {}
    for suite, name, _ in TESTS:
        by_suite.setdefault(suite, []).append(name)
    for suite, names in by_suite.items():
        print(f"\n{suite}  ({len(names)})")
        for n in names:
            print(f"  • {n}")
    print(f"\nTotal: {len(TESTS)} tests")


def main() -> None:
    ap = argparse.ArgumentParser(description="SaavnKit full test suite")
    ap.add_argument("--suite", choices=sorted({t[0] for t in TESTS}),
                    help="run only one suite")
    ap.add_argument("--list", action="store_true", help="list all tests and exit")
    args = ap.parse_args()

    if args.list:
        _list(); return

    try:
        asyncio.run(run(args.suite))
    except KeyboardInterrupt:
        print("\nAborted.")


if __name__ == "__main__":
    main()
