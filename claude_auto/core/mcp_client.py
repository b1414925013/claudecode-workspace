"""MCP 客户端 — 通过 stdio 子进程直连 Playwright MCP（换行分隔 JSON）"""

import json
import logging
import os
import queue
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MCPError(Exception):
    """MCP 通信错误"""


class MCPClient:
    """通过 stdio 子进程与 Playwright MCP 服务器通信

    使用换行分隔 JSON（NDJSON）协议，兼容 Windows 管道。
    """

    def __init__(self, server_cmd: List[str], project_root: str | Path | None = None):
        self.server_cmd = server_cmd
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self._process: Optional[subprocess.Popen] = None
        self._req_id = 0
        self._resp_queue: queue.Queue = queue.Queue()
        self._reader_stop = threading.Event()
        self._reader_thread: Optional[threading.Thread] = None

    # ------------------------------------------------------------------
    # 生命周期
    # ------------------------------------------------------------------

    def __enter__(self):
        self._start_process()
        self._start_reader()
        self._initialize()
        return self

    def __exit__(self, *args):
        self._reader_stop.set()
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=5)
            except Exception:
                try:
                    self._process.kill()
                except Exception:
                    pass
            self._process = None

    # ------------------------------------------------------------------
    # 公共方法
    # ------------------------------------------------------------------

    def list_tools(self) -> List[Dict[str, Any]]:
        return self._request("tools/list", {}).get("tools", [])

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        result = self._request("tools/call", {"name": name, "arguments": arguments})
        return {
            "content": result.get("content", []),
            "isError": result.get("isError", False),
        }

    # ------------------------------------------------------------------
    # 内部
    # ------------------------------------------------------------------

    def _start_process(self):
        env = os.environ.copy()
        # 不需要手动追加 node_path，PATH 中已有
        logger.info("启动 MCP: %s", " ".join(self.server_cmd))
        self._process = subprocess.Popen(
            self.server_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(self.project_root),
            env=env,
        )

    def _start_reader(self):
        """后台线程逐行读取 stdout"""
        self._resp_queue = queue.Queue()
        self._reader_stop.clear()

        def _read():
            buf = b""
            while not self._reader_stop.is_set():
                if not self._process or not self._process.stdout:
                    break
                try:
                    chunk = self._process.stdout.read1(65536)
                except Exception:
                    break
                if not chunk:
                    time.sleep(0.05)
                    continue
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        self._resp_queue.put(data)
                    except json.JSONDecodeError:
                        logger.warning("MCP 解析失败: %s", line[:200])

        self._reader_thread = threading.Thread(target=_read, daemon=True)
        self._reader_thread.start()

    def _initialize(self):
        result = self._request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "claude-auto", "version": "1.0"},
        })
        self._notify("notifications/initialized", {})
        time.sleep(0.3)

    def _request(self, method: str, params: Dict[str, Any]) -> Any:
        self._req_id += 1
        self._send({"jsonrpc": "2.0", "id": self._req_id, "method": method, "params": params})
        return self._wait_response(self._req_id)

    def _notify(self, method: str, params: Dict[str, Any]) -> None:
        self._send({"jsonrpc": "2.0", "method": method, "params": params})

    def _send(self, data: Dict[str, Any]) -> None:
        if not self._process or not self._process.stdin:
            raise MCPError("MCP 服务器未运行")
        raw = json.dumps(data, ensure_ascii=False) + "\n"
        self._process.stdin.write(raw.encode("utf-8"))
        self._process.stdin.flush()

    def _wait_response(self, req_id: int, timeout: float = 120) -> Any:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                msg = self._resp_queue.get(timeout=0.5)
            except queue.Empty:
                if self._process and self._process.poll() is not None:
                    err = ""
                    if self._process.stderr:
                        err = self._process.stderr.read().decode("utf-8", errors="replace")[:500]
                    raise MCPError(f"MCP 已退出: {err}")
                continue
            if "id" not in msg:
                continue
            if msg.get("id") == req_id:
                if "error" in msg:
                    raise MCPError(f"MCP 错误: {msg['error']}")
                return msg.get("result", {})
        raise MCPError(f"MCP 请求超时 (id={req_id})")
