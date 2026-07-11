"""Library backup / restore — JSON + SQLite persistence."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any


def backup_library(data: dict, path: str, format: str = "json") -> str:
    """Persist an entire user library dict to disk."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if format == "json":
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    elif format == "sqlite":
        conn = sqlite3.connect(str(p))
        conn.execute("CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT)")
        for k, v in data.items():
            conn.execute("INSERT OR REPLACE INTO kv VALUES (?, ?)", (k, json.dumps(v, ensure_ascii=False)))
        conn.commit()
        conn.close()
    else:
        raise ValueError(f"Unknown format: {format}")
    return str(p.resolve())


def restore_library(path: str) -> dict:
    p = Path(path)
    if p.suffix == ".json":
        return json.loads(p.read_text(encoding="utf-8"))
    conn = sqlite3.connect(str(p))
    rows = conn.execute("SELECT key, value FROM kv").fetchall()
    conn.close()
    return {k: json.loads(v) for k, v in rows}
