"""Add these lines to your existing JioSaavn/__init__.py to expose the new APIs."""

# --- Smart playback ---
from .Modules.SmartQueue import SmartQueue
from .Utils.Crossfade import crossfade_plan

# --- Analysis ---
from .Analysis.Playlist import analyze_playlist, find_duplicates, infer_mood
from .Analysis.Recommender import recommend_from_history, similar_songs_deep

# --- Sync / backup ---
from .Modules.Sync import sync_spotify_playlist, sync_youtube_playlist
from .Modules.Backup import backup_library, restore_library

# --- Advanced search ---
from .Modules.AdvSearch import fuzzy_search, search_by_lyrics, search_filters

# --- Download Pro ---
from .Modules.DownloadPro import DownloadManager, download_with_lyrics

# --- Discovery ---
from .Modules.Discovery import daily_mix, time_machine, regional_charts, artist_radio

# --- Social / metadata ---
from .Modules.Social import get_song_credits, get_release_calendar, compare_artists

# --- Webhooks ---
from .Modules.Webhooks import WebhookNotifier

__all__ = [
    "SmartQueue", "crossfade_plan",
    "analyze_playlist", "find_duplicates", "infer_mood",
    "recommend_from_history", "similar_songs_deep",
    "sync_spotify_playlist", "sync_youtube_playlist",
    "backup_library", "restore_library",
    "fuzzy_search", "search_by_lyrics", "search_filters",
    "DownloadManager", "download_with_lyrics",
    "daily_mix", "time_machine", "regional_charts", "artist_radio",
    "get_song_credits", "get_release_calendar", "compare_artists",
    "WebhookNotifier",
]
