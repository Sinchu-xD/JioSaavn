"""Crossfade metadata helper — players use these values to blend two tracks."""
from __future__ import annotations


def _dur(v) -> int:
    if v is None: return 0
    if isinstance(v, (int, float)): return int(v)
    s = str(v)
    if ":" in s:
        parts = [int(p) for p in s.split(":") if p.isdigit()]
        m, sec = (parts + [0, 0])[:2]
        return m * 60 + sec
    try: return int(s)
    except ValueError: return 0


def crossfade_plan(current: dict, next_: dict, fade_seconds: int = 6) -> dict:
    """Return a dict with fade timings a player can consume."""
    cur_dur = _dur(current.get("duration"))
    return {
        "current_id": current.get("id") or current.get("songid"),
        "next_id": next_.get("id") or next_.get("songid"),
        "fade_out_start": max(cur_dur - fade_seconds, 0),
        "fade_out_duration": fade_seconds,
        "next_start_offset": 0,
        "next_fade_in": fade_seconds,
    }
