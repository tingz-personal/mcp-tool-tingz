# mcp-tool

[English](#mcp-tool) | [中文](./public/README-zh.md)

---

`mcp-tool` is a small toolkit for building Model Context Protocol (MCP) servers in Python.

It provides a decorator-based tool registry, a JSON-RPC 2.0 handler, and WebSocket / stdio transports so you can expose your tools to MCP-compatible clients.

## Features

- JSON-RPC 2.0 handling with `initialize`, `tools/list`, and `tools/call`
- Async `@tool` decorator for registering MCP tools
- In-memory registry and `/doc` endpoint to list available tools
- WebSocket transport built with FastAPI (`/ws`, `/healthz`, `/doc`)
- stdio transport for local integrations over stdin/stdout
- Typer-based CLI to run your MCP server in `service` or `stdio` mode

## Installation

For local development:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

OR

```bash
pip install mcp-tool-tingz
```

## Defining tools

Use the `@tool` decorator exported from the package:

```python
from mcp_tool import tool

@tool(description="Simple ping tool to verify MCP connectivity")
async def ping(message: str = "pong") -> str:
    return f"MCP: {message}"
```

You can see a more complete example in `mcp-tool/demo_app.py`.

## Running the server

The CLI exposes a single `run` command with two modes: `service` (WebSocket) and `stdio`.

### WebSocket service mode

Start an MCP server over WebSocket:

```bash
mcp-tool run --mode service --host 0.0.0.0 --port 8765 --app mcp_tool.demo_app
```

- `--app` points to a Python module or file that registers tools (via `@tool`).
- The server exposes:
  - `GET /healthz` — health check
  - `GET /doc` — tools documentation (from the registry plus server metadata)
  - `WS /ws` — JSON-RPC 2.0 over WebSocket

You can point an MCP-compatible client at `ws://localhost:8765/ws`.

### stdio mode

To run the same tools over stdio (useful for editor or local CLI integrations):

```bash
mcp-tool run --mode stdio --app mcp_tool.demo_app
```

The process reads and writes JSON-RPC messages framed with `Content-Length` headers on stdin/stdout.

## JSON-RPC protocol

`mcp-tool` follows JSON-RPC 2.0 and implements:

- `initialize` — returns server metadata and capabilities
- `tools/list` (and `tools.list`) — lists all registered tools and their schemas
- `tools/call` (and `tools.call`) — calls a registered tool with arguments

A typical successful response looks like:

```json
{"jsonrpc": "2.0", "id": "uuid", "result": {...}}
```

An error response looks like:

```json
{"jsonrpc": "2.0", "id": "uuid", "error": {"code": -32603, "message": "Internal error"}}
```

## License

This project is licensed under the MIT License. See `LICENSE` for details.

