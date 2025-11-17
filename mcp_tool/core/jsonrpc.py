from __future__ import annotations

import json
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class JSONRPCError(Exception):
    """Error raised for JSON-RPC failures."""

    def __init__(self, code: int, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.code = code
        self.data = data or {}


class JSONRPCResponse(BaseModel):
    """JSON-RPC 2.0 response object."""

    jsonrpc: str = Field(default="2.0", description="JSON-RPC 协议版本")
    result: Dict[str, Any] = Field(description="响应结果数据")
    id: Any = Field(description="请求 ID")


def make_response(result: Dict[str, Any], id_value: Any) -> Dict[str, Any]:
    """Create a JSON-RPC 2.0 response dictionary."""
    return JSONRPCResponse(result=result, id=id_value).model_dump()


def make_error(
    code: int,
    message: str,
    id_value: Any = None,
    data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create a JSON-RPC 2.0 error response dictionary."""
    error: Dict[str, Any] = {"code": code, "message": message}
    if data:
        error["data"] = data
    return {"jsonrpc": "2.0", "id": id_value, "error": error}


def serialize(message: Dict[str, Any]) -> str:
    """Serialize a JSON-RPC message to a compact JSON string."""
    return json.dumps(message, ensure_ascii=False, separators=(",", ":"))


def deserialize(payload: str) -> Dict[str, Any]:
    """Deserialize a JSON string into a JSON-RPC message dictionary."""
    return json.loads(payload)

