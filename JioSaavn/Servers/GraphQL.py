"""GraphQL wrapper over the JioSaavn REST client using Strawberry.

Run:
    pip install strawberry-graphql[fastapi] uvicorn
    uvicorn JioSaavn.Servers.GraphQL:app --reload
"""
from __future__ import annotations
from typing import Any, Optional


def build_schema():
    import strawberry  # type: ignore
    from JioSaavn import JioSaavnClient

    client = JioSaavnClient()

    @strawberry.type
    class Song:
        id: str
        name: str
        duration: Optional[int] = None
        language: Optional[str] = None
        year: Optional[str] = None
        media_url: Optional[str] = None

    def _to_song(s: dict) -> "Song":
        return Song(
            id=str(s.get("id") or s.get("songid") or ""),
            name=str(s.get("name") or s.get("title") or ""),
            duration=s.get("duration"),
            language=s.get("language"),
            year=s.get("year"),
            media_url=s.get("media_url"),
        )

    @strawberry.type
    class Query:
        @strawberry.field
        async def search_songs(self, query: str, limit: int = 10) -> list[Song]:
            r = await client.search_songs(query, limit=limit)
            return [_to_song(s) for s in (r or [])]

        @strawberry.field
        async def song(self, id: str) -> Optional[Song]:
            r = await client.get_song(id)
            return _to_song(r) if r else None

    return strawberry.Schema(query=Query)


def build_app():
    from fastapi import FastAPI  # type: ignore
    from strawberry.fastapi import GraphQLRouter  # type: ignore
    app = FastAPI(title="SaavnAPI GraphQL")
    app.include_router(GraphQLRouter(build_schema()), prefix="/graphql")
    return app


# Lazy: only build when actually served (avoids import-time deps)
app = None  # type: ignore
