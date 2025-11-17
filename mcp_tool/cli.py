from __future__ import annotations

import asyncio
from typing import Optional

import typer
import uvicorn

from .core.service import MCPService
from .transports.stdio import run_stdio
from .transports.websocket import build_app
from .utils import import_app, load_env_file


cli = typer.Typer(help="Run MCP helper service (service or stdio)")


@cli.command()
def run(
    mode: str = typer.Option("service", "--mode", "-m", help="service (websocket) or stdio"),
    host: str = typer.Option("0.0.0.0", "--host"),
    port: int = typer.Option(8765, "--port"),
    name: str = typer.Option("notion-mcp", "--name"),
    version: str = typer.Option("0.1.0", "--version"),
    app_module: Optional[str] = typer.Option(
        None,
        "--app",
        help="Python module or file to import for tool registration",
    ),
    env_file: Optional[str] = typer.Option(None, "--env-file"),
) -> None:
    """Run MCP helper.

    Default mode is WebSocket service per Notion notes; stdio mode is available for Codex CLI.
    """

    load_env_file(env_file)
    import_app(app_module)

    service = MCPService(name=name, version=version)

    if mode == "service":
        app = build_app(service.handle_request, metadata_provider=service.describe)
        uvicorn.run(app, host=host, port=port)
        return

    if mode == "stdio":
        asyncio.run(run_stdio(service.handle_request))
        return

    raise typer.BadParameter("mode must be 'service' or 'stdio'")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()

