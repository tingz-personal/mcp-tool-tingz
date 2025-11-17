from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import uvicorn

# 支持作为脚本直接运行和作为模块导入
try:
    from . import MCPService, tool
    from .transports.stdio import run_stdio
    from .transports.websocket import build_app
except ImportError:
    # 直接运行时，添加父目录到 sys.path
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    from mcp_tool import MCPService, tool
    from mcp_tool.transports.stdio import run_stdio
    from mcp_tool.transports.websocket import build_app


@tool(description="简单的 ping 工具，验证 MCP 连接是否正常", input_schema={"type": "object", "properties": {"message": {"type": "string"}}})
async def ping(message: str = "pong") -> str:
    return f"MCP: {message}"


@tool(
    description="根据关键词搜索示例数据，返回文本内容",
    input_schema={
        "type": "object",
        "properties": {"keyword": {"type": "string"}},
    },
)
async def search(keyword: str = "") -> dict:
    items = [
        {"title": "Notion MCP", "summary": "掌握 JSON-RPC 2.0 和工具注册"},
        {"title": "WebSocket", "summary": "使用 FastAPI 提供双向通讯"},
    ]
    filtered = [item for item in items if keyword.lower() in item["title"].lower()]
    return {"matches": filtered or items}


async def _run_stdio() -> None:
    """启动 stdio 模式，方便在本地 Codex 中集成。"""
    service = MCPService(name="notion-mcp", version="0.1.0")
    await run_stdio(service.handle_request)


def _run_service() -> None:
    """启动 WebSocket 服务模式，提供 /ws 与 /doc 接口。"""
    service = MCPService(name="tingz-mcp", version="0.1.0")
    app = build_app(service.handle_request, metadata_provider=service.describe)
    uvicorn.run(app, host="0.0.0.0", port=8765)


if __name__ == "__main__":
    # 方式一：本地 stdio 集成（如 Codex）
    asyncio.run(_run_stdio())

    # 方式二：WebSocket 服务模式（如 Notion MCP）   
    # _run_service()
