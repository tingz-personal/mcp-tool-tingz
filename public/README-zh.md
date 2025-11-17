# mcp-tool（中文）

---

`mcp-tool` 是一个用来在 Python 中构建 Model Context Protocol（MCP）服务器的小型工具库。

它提供基于装饰器的工具注册、JSON-RPC 2.0 处理器，以及 WebSocket / stdio 传输层，方便你把自定义工具暴露给支持 MCP 的客户端。

## 特性

- 支持 JSON-RPC 2.0 协议，包含 `initialize`、`tools/list` 和 `tools/call`
- 使用异步 `@tool` 装饰器注册 MCP 工具
- 内存中的工具注册表，并通过 `/doc` 接口列出所有可用工具
- 基于 FastAPI 的 WebSocket 传输层（`/ws`、`/healthz`、`/doc`）
- 基于 stdin/stdout 的 stdio 传输层，适合本地集成
- 基于 Typer 的 CLI，可在 `service` 或 `stdio` 模式下运行 MCP 服务器

## 安装

本地开发环境推荐：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```
或者

```bash
pip install mcp-tool-tingz
```

## 定义工具

使用包中导出的 `@tool` 装饰器注册工具：

```python
from mcp_tool import tool

@tool(description="用于验证 MCP 连接是否正常的简单 ping 工具")
async def ping(message: str = "pong") -> str:
    return f"MCP: {message}"
```

更完整的示例可以参考仓库中的 `mcp-tool/demo_app.py`。

## 运行服务器

CLI 暴露了一个 `run` 命令，包含两种模式：`service`（WebSocket）和 `stdio`。

### WebSocket 服务模式

通过 WebSocket 启动 MCP 服务器：

```bash
mcp-tool run --mode service --host 0.0.0.0 --port 8765 --app mcp_tool.demo_app
```

- `--app` 指向注册了工具（通过 `@tool`）的 Python 模块或脚本。
- 服务器会暴露以下接口：
  - `GET /healthz` — 健康检查
  - `GET /doc` — 工具文档（来自工具注册表和服务器元数据）
  - `WS /ws` — 基于 WebSocket 的 JSON-RPC 2.0 通道

你可以将任意支持 MCP 的客户端指向 `ws://localhost:8765/ws`。

### stdio 模式

若希望通过 stdio（如编辑器或本地 CLI）运行同一批工具，可以使用：

```bash
mcp-tool run --mode stdio --app mcp_tool.demo_app
```

该进程会在 stdin/stdout 上按 `Content-Length` 头进行分帧，读写 JSON-RPC 消息。

## JSON-RPC 协议

`mcp-tool` 遵循 JSON-RPC 2.0，并实现以下方法：

- `initialize` —— 返回服务器元数据和能力信息
- `tools/list`（以及 `tools.list`）—— 列出所有已注册工具及其 schema
- `tools/call`（以及 `tools.call`）—— 调用指定工具并传入参数

典型的成功响应格式如下：

```json
{"jsonrpc": "2.0", "id": "uuid", "result": {...}}
```

错误响应格式如下：

```json
{"jsonrpc": "2.0", "id": "uuid", "error": {"code": -32603", "message": "Internal error"}}
```

## 许可证

本项目基于 MIT 许可证开源，详情见仓库根目录的 `LICENSE` 文件。

