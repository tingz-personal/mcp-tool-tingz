from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from ..core.jsonrpc import deserialize, serialize
from ..core.registry import generate_tools_documentation

Handler = Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]
MetadataProvider = Callable[[], Dict[str, Any]]


def build_app(handler: Handler, metadata_provider: MetadataProvider | None = None) -> FastAPI:
    """Build a FastAPI app exposing MCP over WebSocket plus health and docs endpoints."""
    app = FastAPI()

    @app.get("/healthz")
    async def health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.get("/doc")
    async def doc() -> Dict[str, Any]:
        docs = generate_tools_documentation()
        if metadata_provider:
            extra = metadata_provider()
            if isinstance(extra, dict):
                docs.update(extra)
        return docs

    @app.websocket("/ws")
    async def websocket_endpoint(ws: WebSocket) -> None:
        await ws.accept()
        try:
            while True:
                payload = await ws.receive_text()
                request = deserialize(payload)
                response = await handler(request)
                await ws.send_text(serialize(response))
        except WebSocketDisconnect:
            return

    return app

