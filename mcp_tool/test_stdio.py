#!/usr/bin/env python3
"""stdio 模式自动化测试"""

import subprocess
import json
import sys

def send_and_receive(proc, request):
    """发送请求并接收响应"""
    # 序列化
    payload = json.dumps(request, ensure_ascii=False)
    encoded = payload.encode('utf-8')
    
    # 构建消息
    header = f"Content-Length: {len(encoded)}\r\n\r\n"
    full_message = header.encode('utf-8') + encoded
    
    print(f"\n{'='*60}")
    print(f">>> 发送: {request.get('method', 'unknown')} (id: {request.get('id', 'none')})")
    print(f"Content-Length: {len(encoded)}")
    print(f"JSON: {payload}")
    
    # 发送
    try:
        proc.stdin.write(full_message)
        proc.stdin.flush()
    except BrokenPipeError:
        print("\n❌ Broken Pipe: 服务进程已退出")
        # 读取 stderr
        stderr_output = proc.stderr.read().decode('utf-8', errors='ignore')
        if stderr_output:
            print(f"\n[服务端错误]:\n{stderr_output}")
        return None
    
    # 读取响应头
    response_header = b""
    while b"\r\n\r\n" not in response_header:
        chunk = proc.stdout.read(1)
        if not chunk:
            print("\n❌ 没有收到响应，检查服务端错误...")
            # 检查进程是否还在运行
            if proc.poll() is not None:
                print(f"服务进程已退出，退出码: {proc.returncode}")
                stderr_output = proc.stderr.read().decode('utf-8', errors='ignore')
                if stderr_output:
                    print(f"\n[服务端错误]:\n{stderr_output}")
            return None
        response_header += chunk
    
    # 解析 Content-Length
    header_text = response_header.decode('utf-8')
    try:
        content_length = int(header_text.split("Content-Length: ")[1].split("\r\n")[0])
    except (IndexError, ValueError) as e:
        print(f"❌ 无法解析响应头: {header_text!r}")
        return None
    
    # 读取响应体
    body = proc.stdout.read(content_length).decode('utf-8')
    response = json.loads(body)
    
    print(f"\n<<< 响应:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    return response


def main():
    print("="*60)
    print("MCP stdio 自动化测试")
    print("="*60)
    
    # 启动进程 - 使用当前 Python 解释器
    proc = subprocess.Popen(
        [sys.executable, '-m', 'mcp_tool.demo_app'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        # 1. Initialize
        send_and_receive(proc, {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client"}
            }
        })
        
        # 2. List tools
        send_and_receive(proc, {
            "jsonrpc": "2.0",
            "id": "2",
            "method": "tools/list"
        })
        
        # 3. Call ping (默认参数)
        send_and_receive(proc, {
            "jsonrpc": "2.0",
            "id": "3",
            "method": "tools/call",
            "params": {"name": "ping"}
        })
        
        # 4. Call ping (自定义消息)
        send_and_receive(proc, {
            "jsonrpc": "2.0",
            "id": "4",
            "method": "tools/call",
            "params": {"name": "ping", "arguments": {"message": "hello"}}
        })
        
        # 5. Call search
        send_and_receive(proc, {
            "jsonrpc": "2.0",
            "id": "5",
            "method": "tools/call",
            "params": {"name": "search", "arguments": {"keyword": "notion"}}
        })
        
        print(f"\n{'='*60}")
        print("✅ 所有测试完成")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 显示 stderr
        stderr_output = proc.stderr.read().decode('utf-8', errors='ignore')
        if stderr_output:
            print(f"\n[stderr 输出]:\n{stderr_output}")
    
    finally:
        proc.stdin.close()
        proc.terminate()
        proc.wait()


if __name__ == "__main__":
    main()