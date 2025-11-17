from __future__ import annotations

import asyncio
import sys
from typing import Any, Awaitable, Callable, Dict

from ..core.jsonrpc import deserialize, serialize

Handler = Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]


async def _read_message(reader: asyncio.StreamReader) -> Dict[str, Any]:
    headers = {}
    while True:
        line = await reader.readline()
        if not line:
            return {}
        line = line.decode("utf-8")
        if line in ("\r\n", "\n"):
            break
        key, _, value = line.partition(":")
        headers[key.strip().lower()] = value.strip()
    length = int(headers.get("content-length", "0"))
    if length <= 0:
        return {}
    
    # 读取内容
    data = await reader.readexactly(length)
    decoded = data.decode("utf-8")
    
    # 去除开头的空白字符（手动输入时可能多按了回车）
    decoded = decoded.lstrip()
    
    return deserialize(decoded)


async def _write_message(writer: asyncio.StreamWriter, message: Dict[str, Any]) -> None:
    payload = serialize(message)
    encoded = payload.encode("utf-8")
    header = f"Content-Length: {len(encoded)}\r\n\r\n".encode("utf-8")
    writer.write(header + encoded)
    await writer.drain()


async def run_stdio(handler: Handler) -> None:
    loop = asyncio.get_running_loop()

    reader = asyncio.StreamReader()
    reader_protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: reader_protocol, sys.stdin)

    transport, writer_protocol = await loop.connect_write_pipe(asyncio.streams.FlowControlMixin, sys.stdout)
    writer = asyncio.StreamWriter(transport, writer_protocol, reader, loop)

    while True:
        request = await _read_message(reader)
        if not request:
            break
        response = await handler(request)
        await _write_message(writer, response)
