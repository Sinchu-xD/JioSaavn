"""SaavnKit MCP server — expose the API to AI agents (Claude / ChatGPT / Cursor).

Uses the reference `mcp` Python SDK (`pip install mcp`) over stdio.
Run:  python -m JioSaavn.Servers.MCP
"""
from __future__ import annotations
import asyncio
import json


def build_server():
    from mcp.server import Server  # type: ignore
    from mcp.server.stdio import stdio_server  # type: ignore
    from mcp.types import Tool, TextContent  # type: ignore
    from JioSaavn import JioSaavnClient

    client = JioSaavnClient()
    app = Server("saavnkit")

    TOOLS = [
        Tool(name="search_songs", description="Search JioSaavn songs by keyword.",
             inputSchema={"type": "object", "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "default": 10}}, "required": ["query"]}),
        Tool(name="get_song", description="Get a song by JioSaavn song ID.",
             inputSchema={"type": "object", "properties": {"song_id": {"type": "string"}}, "required": ["song_id"]}),
        Tool(name="get_lyrics", description="Fetch lyrics for a song ID.",
             inputSchema={"type": "object", "properties": {"song_id": {"type": "string"}}, "required": ["song_id"]}),
        Tool(name="browse_by_mood", description="Browse songs by mood (romantic, party, chill, ...).",
             inputSchema={"type": "object", "properties": {"mood": {"type": "string"}}, "required": ["mood"]}),
    ]

    @app.list_tools()
    async def _list():
        return TOOLS

    @app.call_tool()
    async def _call(name: str, args: dict):
        fn = getattr(client, name, None)
        if fn is None:
            return [TextContent(type="text", text=json.dumps({"error": f"unknown tool {name}"}))]
        try:
            result = await fn(**args)
        except Exception as e:
            result = {"error": str(e)}
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, default=str))]

    return app, stdio_server


async def main() -> None:
    app, stdio_server = build_server()
    async with stdio_server() as (r, w):
        await app.run(r, w, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
