"""History-based recommender + multi-hop similarity graph."""
from __future__ import annotations
from collections import Counter
from typing import Any


async def recommend_from_history(client: Any, history: list[str], limit: int = 20) -> list[dict]:
    """Given a list of listened song IDs, recommend similar songs."""
    seen = set(history)
    scores: Counter = Counter()
    candidates: dict[str, dict] = {}
    for sid in history[-10:]:
        try:
            sug = await client.get_suggestions(sid, limit=10)
        except Exception:
            continue
        for s in sug or []:
            cid = s.get("id") or s.get("songid")
            if not cid or cid in seen:
                continue
            scores[cid] += 1
            candidates[cid] = s
    ranked = [candidates[cid] for cid, _ in scores.most_common(limit)]
    return ranked


async def similar_songs_deep(client: Any, seed_id: str, hops: int = 2, per_hop: int = 5) -> list[dict]:
    """Walk a similarity graph N hops from a seed song."""
    frontier = [seed_id]
    seen = {seed_id}
    collected: list[dict] = []
    for _ in range(hops):
        next_frontier: list[str] = []
        for sid in frontier:
            try:
                sug = await client.get_suggestions(sid, limit=per_hop)
            except Exception:
                continue
            for s in sug or []:
                cid = s.get("id") or s.get("songid")
                if cid and cid not in seen:
                    seen.add(cid)
                    collected.append(s)
                    next_frontier.append(cid)
        frontier = next_frontier
    return collected
