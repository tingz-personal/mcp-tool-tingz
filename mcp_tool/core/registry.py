from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional


@dataclass
class ToolSpec:
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    handler: Callable[..., Awaitable[Any]]


class ToolRegistry:
    """In-memory registry for MCP tools."""

    def __init__(self) -> None:
        self._tools: Dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        if spec.name in self._tools:
            raise ValueError(f"Tool {spec.name} already registered")
        self._tools[spec.name] = spec

    def list_tools(self) -> Dict[str, ToolSpec]:
        return dict(self._tools)

    def as_list(self) -> List[Dict[str, Any]]:
        """Return tools as a list of JSON-serializable dictionaries."""
        tools: List[Dict[str, Any]] = []
        for spec in self._tools.values():
            tools.append(
                {
                    "name": spec.name,
                    "description": spec.description,
                    "inputSchema": spec.input_schema,
                    "outputSchema": spec.output_schema,
                }
            )
        return tools


_registry = ToolRegistry()


def tool(
    name: Optional[str] = None,
    description: str = "",
    input_schema: Optional[Dict[str, Any]] = None,
    output_schema: Optional[Dict[str, Any]] = None,
) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    """Decorator for registering MCP tools via async callables."""

    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        spec_name = name or func.__name__
        _registry.register(
            ToolSpec(
                name=spec_name,
                description=description or inspect.getdoc(func) or "",
                input_schema=input_schema or {"type": "object", "properties": {}},
                output_schema=output_schema or {"type": "object"},
                handler=func,
            )
        )
        return func

    return decorator


def get_registry() -> ToolRegistry:
    return _registry


def generate_tools_documentation() -> Dict[str, Any]:
    """Build a documentation payload for all registered tools."""
    return {"tools": _registry.as_list()}

