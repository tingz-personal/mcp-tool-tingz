from __future__ import annotations

from typing import Any, Dict

from .jsonrpc import JSONRPCError, make_error, make_response
from .registry import generate_tools_documentation, get_registry


class MCPService:
    """Minimal MCP JSON-RPC handler following Notion MCP notes."""

    def __init__(self, name: str = "notion-mcp", version: str = "0.1.0") -> None:
        self.name = name
        self.version = version

    def describe(self) -> Dict[str, Any]:
        """Return basic server metadata for docs and initialize."""
        return {
            "capabilities": {"tools": True},
            "serverInfo": {"name": self.name, "version": self.version},
        }

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        if request.get("jsonrpc") != "2.0":
            return make_error(-32600, "Invalid Request: jsonrpc must be 2.0", request.get("id"))

        method = request.get("method")
        request_id = request.get("id")

        try:
            if method == "initialize":
                result = await self._initialize(request.get("params") or {})
                return make_response(result, request_id)

            if method in ("tools/list", "tools.list"):
                result = await self._tools_list()
                return make_response(result, request_id)

            if method in ("tools/call", "tools.call"):
                result = await self._tools_call(request.get("params") or {})
                return make_response(result, request_id)

            return make_error(-32601, f"Method not found: {method}", request_id)

        except JSONRPCError as exc:
            return make_error(exc.code, str(exc), request_id, exc.data)
        except Exception as exc:  # noqa: BLE001 - report unexpected errors
            return make_error(-32603, "Internal error", request_id, {"detail": str(exc)})

    async def _initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        payload = self.describe()
        payload["sessionId"] = params.get("sessionId", "local")
        return payload

    async def _tools_list(self) -> Dict[str, Any]:
        return generate_tools_documentation()

    async def _tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        name = params.get("name")
        if not name:
            raise JSONRPCError(-32602, "Missing 'name' for tools/call")

        registry = get_registry().list_tools()
        if name not in registry:
            raise JSONRPCError(-32601, f"Tool not found: {name}")

        spec = registry[name]
        arguments = params.get("arguments") or {}
        result = await spec.handler(**arguments)

        if isinstance(result, dict) and "content" in result:
            return result
        if isinstance(result, str):
            return {"content": [{"type": "text", "text": result}]}
        return {"content": result}

