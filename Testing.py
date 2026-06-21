"""
SaavnAPI Interactive Tester  v2026.6.21
========================================
Run:  python Testing.py

All 27 exported functions are testable via a numbered menu.
Defaults are pre-filled in brackets — just press Enter to accept.
"""

import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from JioSaavn import (
    # Search
    search, search_songs, search_albums, search_artists,
    search_playlists, search_all,
    # Songs
    get_song, get_songs, get_lyrics, get_suggestions, get_radio,
    # URL resolvers
    get_song_by_url, get_album_by_url, get_playlist_by_url,
    # Albums / Playlists / Artists
    get_album, get_playlist,
    get_artist, get_artist_top_songs, get_artist_top_albums,
    # Discovery
    get_trending, get_new_releases, get_top_searches,
    get_charts, get_featured_playlists, get_modules,
    # Client
    JioSaavnClient,
)

# ────────────────────────────────────────────
#  ANSI helpers
# ────────────────────────────────────────────
C  = "\033[96m"   # cyan
G  = "\033[92m"   # green
Y  = "\033[93m"   # yellow
R  = "\033[91m"   # red
B  = "\033[1m"    # bold
D  = "\033[2m"    # dim
M  = "\033[95m"   # magenta
O  = "\033[38;5;208m"  # orange
Z  = "\033[0m"    # reset

def hdr(text):
    w = 60
    print(f"\n{B}{C}{'─'*w}\n  {text}\n{'─'*w}{Z}")

def ok(t):   print(f"{G}  ✅  {t}{Z}")
def err(t):  print(f"{R}  ❌  {t}{Z}")
def tip(t):  print(f"{D}  ℹ   {t}{Z}")
def sub(t):  print(f"{M}  ›   {t}{Z}")

def ask(label, default=""):
    suf = f" {D}[{default}]{Z}" if default else ""
    val = input(f"{Y}  → {label}{suf}: {Z}").strip()
    return val if val else default

def pretty(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False)

def show_song(s, i=None):
    pre = f"  {B}{i:>2}.{Z} " if i is not None else "  "
    print(f"{pre}{B}{s.get('song','?')}{Z}  —  {s.get('primary_artists','?')}")
    print(f"      {D}id={s.get('id')}  dur={s.get('duration','?')}  lang={s.get('language','?')}  lyrics={s.get('has_lyrics')}{Z}")

def show_album(a, i=None):
    pre = f"  {B}{i:>2}.{Z} " if i is not None else "  "
    print(f"{pre}{B}{a.get('name', a.get('title','?'))}{Z}  ({a.get('year','?')})")
    print(f"      {D}id={a.get('id')}  artists={a.get('primary_artists','?')}  songs={a.get('song_count','?')}{Z}")

def show_artist(a, i=None):
    pre = f"  {B}{i:>2}.{Z} " if i is not None else "  "
    print(f"{pre}{B}{a.get('name','?')}{Z}")
    print(f"      {D}id={a.get('id')}  type={a.get('dominant_type','?')}  lang={a.get('dominant_language','?')}{Z}")

def show_playlist(p, i=None):
    pre = f"  {B}{i:>2}.{Z} " if i is not None else "  "
    name = p.get('name') or p.get('listname') or p.get('title','?')
    print(f"{pre}{B}{name}{Z}")
    print(f"      {D}id={p.get('id')}  songs={p.get('song_count','?')}  followers={p.get('follower_count','?')}{Z}")

def show_item(item, i=None):
    t = item.get("type","?")
    pre = f"  {B}{i:>2}.{Z} " if i is not None else "  "
    print(f"{pre}{B}{item.get('title','?')}{Z}  {D}[{t}]{Z}")
    print(f"      {D}id={item.get('id')}  lang={item.get('language','?')}  release={item.get('release_date','?')}{Z}")

# ────────────────────────────────────────────
#  Test functions
# ────────────────────────────────────────────

async def t_search():
    hdr("🔍  search(query)")
    q     = ask("Query", "Arijit Singh")
    limit = int(ask("Limit", "5"))
    lyr   = ask("Lyrics? (y/n)", "n").lower() == "y"
    songs = await search(q, limit=limit, lyrics=lyr)
    ok(f"{len(songs)} songs") if songs else err("No results")
    for i, s in enumerate(songs, 1): show_song(s, i)

async def t_search_songs():
    hdr("🔍  search_songs(query, page)")
    q     = ask("Query", "Pritam")
    limit = int(ask("Limit", "5"))
    page  = int(ask("Page", "1"))
    songs = await search_songs(q, limit=limit, page=page)
    ok(f"{len(songs)} songs (page {page})") if songs else err("No results")
    for i, s in enumerate(songs, 1): show_song(s, i)

async def t_search_albums():
    hdr("💿  search_albums(query)")
    q     = ask("Query", "Rockstar")
    limit = int(ask("Limit", "5"))
    albums = await search_albums(q, limit=limit)
    ok(f"{len(albums)} albums") if albums else err("No results")
    for i, a in enumerate(albums, 1): show_album(a, i)

async def t_search_artists():
    hdr("👤  search_artists(query)")
    q     = ask("Artist name", "A.R. Rahman")
    limit = int(ask("Limit", "5"))
    arts  = await search_artists(q, limit=limit)
    ok(f"{len(arts)} artists") if arts else err("No results")
    for i, a in enumerate(arts, 1): show_artist(a, i)

async def t_search_playlists():
    hdr("📋  search_playlists(query)")
    q     = ask("Query", "Bollywood Hits")
    limit = int(ask("Limit", "5"))
    pls   = await search_playlists(q, limit=limit)
    ok(f"{len(pls)} playlists") if pls else err("No results")
    for i, p in enumerate(pls, 1): show_playlist(p, i)

async def t_search_all():
    hdr("🌐  search_all(query)  — all categories in parallel")
    q     = ask("Query", "Arijit Singh")
    limit = int(ask("Limit per category", "3"))
    res   = await search_all(q, limit=limit)
    print()
    sub(f"Songs ({len(res['songs'])})")
    for i, s in enumerate(res["songs"], 1): show_song(s, i)
    sub(f"Albums ({len(res['albums'])})")
    for i, a in enumerate(res["albums"], 1): show_album(a, i)
    sub(f"Artists ({len(res['artists'])})")
    for i, a in enumerate(res["artists"], 1): show_artist(a, i)
    sub(f"Playlists ({len(res['playlists'])})")
    for i, p in enumerate(res["playlists"], 1): show_playlist(p, i)

async def t_get_song():
    hdr("🎵  get_song(song_id)")
    tip("Use search() to find a song ID first")
    sid = ask("Song ID", "aRZbUYD7")
    lyr = ask("Lyrics? (y/n)", "n").lower() == "y"
    s   = await get_song(sid, lyrics=lyr)
    if not s: err("Not found — check the ID"); return
    ok(f"{s['song']}")
    for k in ["id","song","album","primary_artists","featured_artists",
              "duration","year","release_date","language","label",
              "has_lyrics","explicit","views","copyright"]:
        v = s.get(k)
        if v not in (None,"",False):
            print(f"  {B}{k:22}{Z} {v}")
    if s.get("media_url"):
        print(f"\n  {B}{'media_url':22}{Z} {G}{s['media_url'][:90]}...{Z}")
    if lyr and s.get("lyrics"):
        print(f"\n  {B}Lyrics (preview):{Z}\n  {D}{s['lyrics'][:400]}...{Z}")

async def t_get_songs():
    hdr("📦  get_songs(song_ids)  — batch fetch")
    tip("Enter comma-separated IDs")
    raw  = ask("Song IDs", "aRZbUYD7,4ZSL1xJk,FpxaLHiB")
    ids  = [x.strip() for x in raw.split(",") if x.strip()]
    songs = await get_songs(ids)
    ok(f"Fetched {len(songs)}/{len(ids)} songs") if songs else err("None fetched")
    for i, s in enumerate(songs, 1): show_song(s, i)

async def t_get_lyrics():
    hdr("📝  get_lyrics(song_id)")
    sid = ask("Song ID", "aRZbUYD7")
    lyr = await get_lyrics(sid)
    if lyr:
        ok(f"{len(lyr)} chars")
        print(f"\n{lyr[:700]}")
        if len(lyr) > 700: print(f"\n{D}  ...({len(lyr)-700} more chars){Z}")
    else:
        err("No lyrics for this song")

async def t_get_suggestions():
    hdr("🎯  get_suggestions(song_id)")
    sid   = ask("Song ID", "aRZbUYD7")
    limit = int(ask("Limit", "5"))
    recs  = await get_suggestions(sid, limit=limit)
    ok(f"{len(recs)} suggestions") if recs else err("None found")
    for i, s in enumerate(recs, 1): show_song(s, i)

async def t_get_radio():
    hdr("📻  get_radio(song_id)  — seeded radio station")
    tip("Creates a JioSaavn radio station and returns its queue")
    sid   = ask("Seed Song ID", "aRZbUYD7")
    limit = int(ask("Tracks to return (1-25)", "10"))
    tracks = await get_radio(sid, limit=limit)
    if tracks:
        ok(f"{len(tracks)} radio tracks")
        for i, s in enumerate(tracks, 1): show_song(s, i)
    else:
        err("Radio returned nothing. Station creation may have failed.")

async def t_get_song_by_url():
    hdr("🔗  get_song_by_url(url)")
    tip("Paste any jiosaavn.com/song/... URL")
    url = ask("URL", "https://www.jiosaavn.com/song/tum-hi-ho/aRZbUYD7")
    lyr = ask("Lyrics? (y/n)", "n").lower() == "y"
    s   = await get_song_by_url(url, lyrics=lyr)
    if s:
        ok(f"{s['song']}  —  {s['primary_artists']}")
        print(f"  {D}id={s['id']}  dur={s['duration']}  lang={s['language']}{Z}")
    else:
        err("Could not resolve URL — check the link")

async def t_get_album_by_url():
    hdr("🔗  get_album_by_url(url)")
    tip("Paste any jiosaavn.com/album/... URL")
    url   = ask("URL", "https://www.jiosaavn.com/album/rockstar/OelUBDQMMXc_")
    album = await get_album_by_url(url)
    if album:
        ok(f"{album.get('name','?')}  ({album.get('year','?')})")
        print(f"  {D}id={album.get('id')}  songs={album.get('song_count')}  lang={album.get('language')}{Z}")
    else:
        err("Could not resolve URL")

async def t_get_playlist_by_url():
    hdr("🔗  get_playlist_by_url(url)")
    tip("Paste any jiosaavn.com/featured/... URL")
    url = ask("URL", "https://www.jiosaavn.com/featured/top-50-songs/AbCdEfGhIjK")
    pl  = await get_playlist_by_url(url)
    if pl:
        ok(f"{pl.get('listname','?')}  songs={pl.get('song_count','?')}")
    else:
        err("Could not resolve URL")

async def t_get_artist():
    hdr("👤  get_artist(artist_id)")
    tip("Needs numeric ID — use search_artists() to find it")
    aid    = ask("Numeric Artist ID", "459320")
    n_song = int(ask("Top songs", "5"))
    n_alb  = int(ask("Top albums", "3"))
    artist = await get_artist(aid, n_song=n_song, n_album=n_alb)
    if not artist: err("Not found — use a numeric ID"); return
    ok(f"{artist['name']}")
    for k in ["id","name","dominant_type","dominant_language",
              "follower_count","fan_count","is_verified","dob"]:
        v = artist.get(k)
        if v not in (None,"",[]): print(f"  {B}{k:24}{Z} {v}")
    for lk in ["twitter","fb","wiki"]:
        if artist.get(lk): print(f"  {B}{lk:24}{Z} {artist[lk]}")
    if artist.get("bio"):
        print(f"\n  {B}Bio:{Z}\n  {D}{artist['bio'][:300]}...{Z}")
    if artist.get("top_songs"):
        print(f"\n  {B}Top Songs:{Z}")
        for i, s in enumerate(artist["top_songs"], 1): show_song(s, i)
    if artist.get("top_albums"):
        print(f"\n  {B}Top Albums:{Z}")
        for i, a in enumerate(artist["top_albums"], 1): show_album(a, i)
    if artist.get("similar_artists"):
        names = [a.get("name","") for a in artist["similar_artists"][:5]]
        print(f"\n  {B}Similar Artists:{Z} {', '.join(names)}")

async def t_get_artist_top_songs():
    hdr("🎵  get_artist_top_songs(artist_id)")
    aid      = ask("Numeric Artist ID", "459320")
    page     = int(ask("Page", "1"))
    cat      = ask("Category (popularity/latest/alphabetical)", "popularity")
    sort     = ask("Sort (asc/desc)", "desc")
    songs    = await get_artist_top_songs(aid, page=page, category=cat, sort_order=sort)
    ok(f"{len(songs)} songs") if songs else err("None found")
    for i, s in enumerate(songs, 1): show_song(s, i)

async def t_get_artist_top_albums():
    hdr("💿  get_artist_top_albums(artist_id)")
    aid    = ask("Numeric Artist ID", "459320")
    page   = int(ask("Page", "1"))
    albums = await get_artist_top_albums(aid, page=page)
    ok(f"{len(albums)} albums") if albums else err("None found")
    for i, a in enumerate(albums, 1): show_album(a, i)

async def t_get_album():
    hdr("💿  get_album(album_id)")
    aid   = ask("Album ID", "14284038")
    album = await get_album(aid)
    if not album: err("Not found"); return
    ok(f"{album.get('name','?')}")
    for k in ["id","name","primary_artists","year","language","label","song_count","copyright"]:
        v = album.get(k)
        if v not in (None,""): print(f"  {B}{k:20}{Z} {v}")
    if album.get("songs"):
        print(f"\n  {B}Tracks:{Z}")
        for i, s in enumerate(album["songs"], 1): show_song(s, i)

async def t_get_playlist():
    hdr("📋  get_playlist(list_id)")
    pid = ask("Playlist ID", "159144718")
    pl  = await get_playlist(pid)
    if not pl: err("Not found"); return
    ok(f"{pl.get('listname','?')}")
    for k in ["id","listname","firstname","song_count","follower_count","language","play_count"]:
        v = pl.get(k)
        if v not in (None,""): print(f"  {B}{k:20}{Z} {v}")
    if pl.get("songs"):
        print(f"\n  {B}Songs (first 10):{Z}")
        for i, s in enumerate(pl["songs"][:10], 1): show_song(s, i)

async def t_get_trending():
    hdr("🔥  get_trending(language, limit)")
    lang  = ask("Language (hindi/english/punjabi/all)", "hindi")
    limit = int(ask("Limit", "10"))
    items = await get_trending(language=None if lang=="all" else lang, limit=limit)
    ok(f"{len(items)} trending items") if items else err("None")
    for i, item in enumerate(items, 1): show_item(item, i)

async def t_get_new_releases():
    hdr("🆕  get_new_releases(language, limit)")
    lang  = ask("Language (hindi/english/all)", "hindi")
    limit = int(ask("Limit", "10"))
    items = await get_new_releases(language=None if lang=="all" else lang, limit=limit)
    ok(f"{len(items)} new releases") if items else err("None")
    for i, item in enumerate(items, 1): show_item(item, i)

async def t_get_top_searches():
    hdr("🔎  get_top_searches()")
    limit = int(ask("Limit", "10"))
    terms = await get_top_searches(limit=limit)
    if terms:
        ok(f"{len(terms)} top search terms")
        for i, t in enumerate(terms, 1): print(f"  {B}{i:>2}.{Z}  {t}")
    else:
        err("None returned")

async def t_get_charts():
    hdr("📊  get_charts()")
    charts = await get_charts()
    ok(f"{len(charts)} charts") if charts else err("None")
    for i, c in enumerate(charts, 1): show_playlist(c, i)
    tip("Copy an id → use get_playlist() to fetch all songs")

async def t_get_featured_playlists():
    hdr("⭐  get_featured_playlists(language, limit)")
    lang  = ask("Language (hindi/english/all)", "all")
    limit = int(ask("Limit", "10"))
    pls   = await get_featured_playlists(language=None if lang=="all" else lang, limit=limit)
    ok(f"{len(pls)} playlists") if pls else err("None")
    for i, p in enumerate(pls, 1): show_playlist(p, i)

async def t_get_modules():
    hdr("🏠  get_modules()  — all homepage data in one call")
    lang  = ask("Language (hindi/english/all)", "hindi")
    limit = int(ask("Items per section", "5"))
    mods  = await get_modules(language=None if lang=="all" else lang, limit=limit)
    print()
    for section, items in mods.items():
        sub(f"{section.upper()}  ({len(items)} items)")
        for item in items:
            print(f"    {B}{item.get('title','?')}{Z}  {D}[{item.get('type','?')}]  id={item.get('id')}{Z}")

async def t_batch_client():
    hdr("⚡  JioSaavnClient  — batch on one shared session")
    q     = ask("Search query", "Arijit Singh")
    limit = int(ask("Limit", "3"))
    print()
    async with JioSaavnClient() as client:
        songs, charts, mods, trending = await asyncio.gather(
            search(q, limit=limit, client=client),
            get_charts(client=client),
            get_modules(language="hindi", limit=5, client=client),
            get_trending(limit=5, client=client),
        )
    ok(f"search → {len(songs)} songs")
    for s in songs: show_song(s)
    ok(f"charts → {len(charts)} charts")
    ok(f"modules → trending={len(mods['trending'])}  releases={len(mods['new_releases'])}")
    ok(f"trending → {len(trending)} items")
    print(f"\n  {G}All 4 calls on a single shared session ✅{Z}")

async def t_raw_json():
    hdr("🛠️   Raw JSON output for any function")
    print(f"""
  {B} 1{Z}  search          {B} 2{Z}  get_song        {B} 3{Z}  get_songs (batch)
  {B} 4{Z}  get_artist      {B} 5{Z}  get_album       {B} 6{Z}  get_playlist
  {B} 7{Z}  get_trending    {B} 8{Z}  get_charts      {B} 9{Z}  get_suggestions
  {B}10{Z}  get_radio       {B}11{Z}  search_all      {B}12{Z}  get_modules
  {B}13{Z}  get_top_searches
""")
    choice = ask("Choice", "1")
    result = None
    if   choice == "1":  result = await search(ask("Query","Hawa Hawa"), limit=3)
    elif choice == "2":  result = await get_song(ask("Song ID","aRZbUYD7"))
    elif choice == "3":
        raw = ask("IDs (comma-sep)", "aRZbUYD7,4ZSL1xJk")
        result = await get_songs([x.strip() for x in raw.split(",")])
    elif choice == "4":  result = await get_artist(ask("Artist ID","459320"), n_song=3, n_album=2)
    elif choice == "5":  result = await get_album(ask("Album ID","14284038"))
    elif choice == "6":  result = await get_playlist(ask("Playlist ID","159144718"))
    elif choice == "7":  result = await get_trending(limit=5)
    elif choice == "8":  result = await get_charts()
    elif choice == "9":  result = await get_suggestions(ask("Song ID","aRZbUYD7"), limit=5)
    elif choice == "10": result = await get_radio(ask("Song ID","aRZbUYD7"), limit=5)
    elif choice == "11": result = await search_all(ask("Query","Arijit Singh"), limit=3)
    elif choice == "12": result = await get_modules(limit=5)
    elif choice == "13": result = await get_top_searches(limit=10)

    if result is not None:
        print()
        print(pretty(result))
    else:
        err("No result")

# ────────────────────────────────────────────
#  Menu definition
# ────────────────────────────────────────────

MENU = [
    # ── Search ──────────────────────────────
    ("search()",                      t_search),
    ("search_songs()   paginated",    t_search_songs),
    ("search_albums()",               t_search_albums),
    ("search_artists()",              t_search_artists),
    ("search_playlists()",            t_search_playlists),
    ("search_all()     all categories at once",  t_search_all),
    # ── Songs ───────────────────────────────
    ("get_song(song_id)",             t_get_song),
    ("get_songs(ids)   batch fetch",  t_get_songs),
    ("get_lyrics(song_id)",           t_get_lyrics),
    ("get_suggestions(song_id)",      t_get_suggestions),
    ("get_radio(song_id)  📻  NEW",   t_get_radio),
    # ── URL Resolvers ────────────────────────
    ("get_song_by_url(url)    🔗 NEW", t_get_song_by_url),
    ("get_album_by_url(url)   🔗 NEW", t_get_album_by_url),
    ("get_playlist_by_url(url)🔗 NEW", t_get_playlist_by_url),
    # ── Artists ─────────────────────────────
    ("get_artist(artist_id)",         t_get_artist),
    ("get_artist_top_songs()",        t_get_artist_top_songs),
    ("get_artist_top_albums()",       t_get_artist_top_albums),
    # ── Albums / Playlists ──────────────────
    ("get_album(album_id)",           t_get_album),
    ("get_playlist(list_id)",         t_get_playlist),
    # ── Discovery ───────────────────────────
    ("get_trending()",                t_get_trending),
    ("get_new_releases()",            t_get_new_releases),
    ("get_top_searches()    NEW",     t_get_top_searches),
    ("get_charts()",                  t_get_charts),
    ("get_featured_playlists()",      t_get_featured_playlists),
    ("get_modules()   🏠  NEW",       t_get_modules),
    # ── Power tools ─────────────────────────
    ("JioSaavnClient  ⚡  batch",     t_batch_client),
    ("Raw JSON output",               t_raw_json),
]

# ────────────────────────────────────────────
#  Main loop
# ────────────────────────────────────────────

BANNER = f"""
{B}{C}╔══════════════════════════════════════════════════════════╗
║       SaavnAPI Interactive Tester   v2026.6.21           ║
║       27 functions  ·  fully tested  ·  async            ║
╚══════════════════════════════════════════════════════════╝{Z}
"""

def print_menu():
    print(BANNER)
    col1, col2 = [], []
    for i, (label, _) in enumerate(MENU, 1):
        entry = f"  {B}{i:>2}.{Z}  {label}"
        (col1 if i <= (len(MENU)+1)//2 else col2).append(entry)
    for a, b in zip(col1, col2 + [""]):
        print(f"{a:<55}{b}")
    print(f"\n   {B} 0.{Z}  Exit\n")


async def main():
    while True:
        print_menu()
        try:
            raw = input(f"{Y}  Choose (0-{len(MENU)}): {Z}").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{D}  Bye!{Z}\n")
            break

        if raw in ("0", "q", "quit", "exit"):
            print(f"\n{D}  Bye!{Z}\n")
            break

        try:
            choice = int(raw)
        except ValueError:
            print(f"{R}  Enter a number 0–{len(MENU)}{Z}")
            continue

        if not 1 <= choice <= len(MENU):
            print(f"{R}  Out of range{Z}")
            continue

        label, fn = MENU[choice - 1]
        try:
            await fn()
        except ValueError as e:
            err(f"Invalid input: {e}")
        except Exception as e:
            err(f"Error: {e}")
            import traceback; traceback.print_exc()

        input(f"\n{D}  Press Enter to return to menu...{Z}")


if __name__ == "__main__":
    asyncio.run(main())
