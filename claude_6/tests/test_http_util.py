"""HttpUtil 单元测试。

使用 ``httpx.MockTransport`` 模拟 HTTP 服务，不发起真实网络请求。
"""

from __future__ import annotations

import json as _json
from pathlib import Path
from typing import Any

import pytest

from pyhutool.core.exceptions import UtilError
from pyhutool.http import AsyncHttpUtil, HttpResponse, HttpUtil

httpx_available = True
try:
    import httpx
    from httpx import MockTransport
except ImportError:
    httpx_available = False

pytestmark = pytest.mark.skipif(not httpx_available, reason="需要 httpx")


# ---------------------------------------------------------------------
# 工具：构造 MockTransport 处理器
# ---------------------------------------------------------------------
def _make_transport(handler: Any) -> Any:
    """构造 MockTransport 实例。"""
    return MockTransport(handler)


def _json_handler(payload: Any, status: int = 200) -> Any:
    """返回 JSON 响应的处理器工厂。"""
    def handler(request: Any) -> Any:
        return httpx.Response(status, json=payload)
    return handler


def _text_handler(text: str, status: int = 200, content_type: str = "text/plain") -> Any:
    """返回文本响应的处理器工厂。"""
    def handler(request: Any) -> Any:
        return httpx.Response(status, text=text, headers={"Content-Type": content_type})
    return handler


def _bytes_handler(payload: bytes, status: int = 200) -> Any:
    """返回字节响应的处理器工厂。"""
    def handler(request: Any) -> Any:
        return httpx.Response(status, content=payload)
    return handler


# ---------------------------------------------------------------------
# 夹具：注入 MockTransport
# ---------------------------------------------------------------------
@pytest.fixture
def mock_sync(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """注入同步 ``httpx.Client`` 的 MockTransport。

    返回一个 ``calls`` 字典，记录所有请求。
    """
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        # 默认返回 200 + {"ok": True}，可被特定 case 覆盖
        return httpx.Response(200, json={"ok": True, "method": request.method})

    transport = MockTransport(handler)
    original_client = httpx.Client

    def patched_client(*args: Any, **kwargs: Any) -> Any:
        kwargs.setdefault("transport", transport)
        return original_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "Client", patched_client)
    return {"calls": calls, "transport": transport}


@pytest.fixture
def mock_async(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """注入异步 ``httpx.AsyncClient`` 的 MockTransport。"""
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json={"ok": True, "method": request.method})

    transport = MockTransport(handler)
    original_client = httpx.AsyncClient

    def patched_client(*args: Any, **kwargs: Any) -> Any:
        kwargs.setdefault("transport", transport)
        return original_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", patched_client)
    return {"calls": calls, "transport": transport}


# ---------------------------------------------------------------------
# HttpResponse 单元测试
# ---------------------------------------------------------------------
class TestHttpResponse:
    """HttpResponse 包装类。"""

    def test_status(self) -> None:
        raw = httpx.Response(200, text="ok")
        resp = HttpResponse(raw)
        assert resp.status == 200
        assert resp.status_code == 200

    def test_is_success(self) -> None:
        assert HttpResponse(httpx.Response(200)).is_success is True
        assert HttpResponse(httpx.Response(204)).is_success is True
        assert HttpResponse(httpx.Response(300)).is_success is False
        assert HttpResponse(httpx.Response(404)).is_success is False

    def test_is_ok_alias(self) -> None:
        assert HttpResponse(httpx.Response(200)).is_ok is True

    def test_is_redirect(self) -> None:
        assert HttpResponse(httpx.Response(301)).is_redirect is True
        assert HttpResponse(httpx.Response(200)).is_redirect is False

    def test_is_client_error(self) -> None:
        assert HttpResponse(httpx.Response(404)).is_client_error is True
        assert HttpResponse(httpx.Response(500)).is_client_error is False

    def test_is_server_error(self) -> None:
        assert HttpResponse(httpx.Response(500)).is_server_error is True
        assert HttpResponse(httpx.Response(404)).is_server_error is False

    def test_text_body(self) -> None:
        raw = httpx.Response(200, text="hello")
        resp = HttpResponse(raw)
        assert resp.text == "hello"
        assert resp.body == "hello"

    def test_content_body_bytes(self) -> None:
        raw = httpx.Response(200, content=b"\x00\x01")
        resp = HttpResponse(raw)
        assert resp.content == b"\x00\x01"
        assert resp.body_bytes == b"\x00\x01"

    def test_headers(self) -> None:
        raw = httpx.Response(200, headers={"X-Custom": "v"})
        resp = HttpResponse(raw)
        assert resp.headers["X-Custom"] == "v"
        assert resp.header("X-Custom") == "v"
        assert resp.header("Missing", default="d") == "d"

    def test_content_type(self) -> None:
        raw = httpx.Response(200, text="x", headers={"Content-Type": "application/json"})
        assert HttpResponse(raw).content_type == "application/json"

    def test_json(self) -> None:
        # 依赖 orjson，若未装会跳过本用例
        orjson_ok = True
        try:
            import orjson  # noqa: F401
        except ImportError:
            orjson_ok = False
        if not orjson_ok:
            pytest.skip("需要 orjson")
        raw = httpx.Response(200, json={"a": 1})
        resp = HttpResponse(raw)
        assert resp.json() == {"a": 1}

    def test_url(self) -> None:
        raw = httpx.Response(200, request=httpx.Request("GET", "https://example.com/x"))
        assert HttpResponse(raw).url == "https://example.com/x"

    def test_raise_for_status_ok(self) -> None:
        resp = HttpResponse(httpx.Response(200))
        # 不应抛错
        resp.raise_for_status()

    def test_raise_for_status_error(self) -> None:
        resp = HttpResponse(httpx.Response(404))
        with pytest.raises(UtilError):
            resp.raise_for_status()

    def test_repr(self) -> None:
        resp = HttpResponse(httpx.Response(200))
        assert "HttpResponse" in repr(resp)
        assert "200" in repr(resp)


# ---------------------------------------------------------------------
# HttpUtil 同步测试
# ---------------------------------------------------------------------
class TestSyncHttpUtil:
    """HttpUtil 同步。"""

    def test_get_basic(self, mock_sync: dict[str, Any]) -> None:
        resp = HttpUtil.get("https://example.com/")
        assert resp.status == 200
        assert resp.json()["ok"] is True
        assert mock_sync["calls"][0].method == "GET"

    def test_get_with_params(self, mock_sync: dict[str, Any]) -> None:
        HttpUtil.get("https://example.com/", params={"q": "hutool", "n": "1"})
        call = mock_sync["calls"][0]
        assert "q=hutool" in str(call.url)
        assert "n=1" in str(call.url)

    def test_get_with_headers(self, mock_sync: dict[str, Any]) -> None:
        HttpUtil.get("https://example.com/", headers={"X-Token": "abc"})
        assert mock_sync["calls"][0].headers["X-Token"] == "abc"

    def test_get_default_user_agent(self, mock_sync: dict[str, Any]) -> None:
        HttpUtil.get("https://example.com/")
        ua = mock_sync["calls"][0].headers.get("User-Agent", "")
        assert "pyhutool" in ua

    def test_get_custom_user_agent(self, mock_sync: dict[str, Any]) -> None:
        HttpUtil.get("https://example.com/", user_agent="custom/1.0")
        assert mock_sync["calls"][0].headers["User-Agent"] == "custom/1.0"

    def test_post_json(self, mock_sync: dict[str, Any]) -> None:
        resp = HttpUtil.post("https://example.com/", json={"k": "v"})
        assert resp.status == 200
        body = mock_sync["calls"][0].content
        assert _json.loads(body) == {"k": "v"}
        # 默认 Content-Type 由 httpx 自动设置
        assert mock_sync["calls"][0].headers["Content-Type"] == "application/json"

    def test_post_form(self, mock_sync: dict[str, Any]) -> None:
        HttpUtil.post("https://example.com/", data={"k": "v"})
        ct = mock_sync["calls"][0].headers["Content-Type"]
        assert "application/x-www-form-urlencoded" in ct

    def test_post_raw_content(self, mock_sync: dict[str, Any]) -> None:
        HttpUtil.post("https://example.com/", content=b"raw-bytes")
        assert mock_sync["calls"][0].content == b"raw-bytes"

    def test_put(self, mock_sync: dict[str, Any]) -> None:
        HttpUtil.put("https://example.com/", json={"k": "v"})
        assert mock_sync["calls"][0].method == "PUT"

    def test_delete(self, mock_sync: dict[str, Any]) -> None:
        HttpUtil.delete("https://example.com/")
        assert mock_sync["calls"][0].method == "DELETE"

    def test_patch(self, mock_sync: dict[str, Any]) -> None:
        HttpUtil.patch("https://example.com/", json={"k": "v"})
        assert mock_sync["calls"][0].method == "PATCH"

    def test_head(self, mock_sync: dict[str, Any]) -> None:
        HttpUtil.head("https://example.com/")
        assert mock_sync["calls"][0].method == "HEAD"

    def test_options(self, mock_sync: dict[str, Any]) -> None:
        HttpUtil.options("https://example.com/")
        assert mock_sync["calls"][0].method == "OPTIONS"

    def test_request_method_uppercased(self, mock_sync: dict[str, Any]) -> None:
        HttpUtil.request("get", "https://example.com/")
        assert mock_sync["calls"][0].method == "GET"

    def test_auth_basic(self, mock_sync: dict[str, Any]) -> None:
        HttpUtil.get("https://example.com/", auth=("alice", "secret"))
        auth_header = mock_sync["calls"][0].headers.get("Authorization", "")
        assert auth_header.startswith("Basic ")

    def test_cookies(self, mock_sync: dict[str, Any]) -> None:
        HttpUtil.get("https://example.com/", cookies={"session": "abc"})
        cookie_header = mock_sync["calls"][0].headers.get("Cookie", "")
        assert "session=abc" in cookie_header

    def test_timeout_passed_through(self, mock_sync: dict[str, Any]) -> None:
        # 仅验证不抛错（无法直接断言 timeout 值，因 MockTransport 不应用 timeout）
        HttpUtil.get("https://example.com/", timeout=5.0)

    def test_no_user_agent(self, mock_sync: dict[str, Any]) -> None:
        HttpUtil.get("https://example.com/", user_agent=None)
        # user_agent=None 时不设置 User-Agent
        assert "User-Agent" not in mock_sync["calls"][0].headers or (
            mock_sync["calls"][0].headers["User-Agent"].startswith("python-httpx")
            or mock_sync["calls"][0].headers["User-Agent"].startswith("pyhutool") is False
        )


# ---------------------------------------------------------------------
# AsyncHttpUtil 异步测试
# ---------------------------------------------------------------------
class TestAsyncHttpUtil:
    """AsyncHttpUtil 异步。"""

    @pytest.mark.asyncio
    async def test_get_basic(self, mock_async: dict[str, Any]) -> None:
        resp = await AsyncHttpUtil.get("https://example.com/")
        assert resp.status == 200
        assert resp.json()["ok"] is True
        assert mock_async["calls"][0].method == "GET"

    @pytest.mark.asyncio
    async def test_post_json(self, mock_async: dict[str, Any]) -> None:
        resp = await AsyncHttpUtil.post("https://example.com/", json={"k": "v"})
        assert resp.status == 200
        body = mock_async["calls"][0].content
        assert _json.loads(body) == {"k": "v"}

    @pytest.mark.asyncio
    async def test_put(self, mock_async: dict[str, Any]) -> None:
        await AsyncHttpUtil.put("https://example.com/", json={"k": "v"})
        assert mock_async["calls"][0].method == "PUT"

    @pytest.mark.asyncio
    async def test_delete(self, mock_async: dict[str, Any]) -> None:
        await AsyncHttpUtil.delete("https://example.com/")
        assert mock_async["calls"][0].method == "DELETE"

    @pytest.mark.asyncio
    async def test_patch(self, mock_async: dict[str, Any]) -> None:
        await AsyncHttpUtil.patch("https://example.com/", json={"k": "v"})
        assert mock_async["calls"][0].method == "PATCH"

    @pytest.mark.asyncio
    async def test_head(self, mock_async: dict[str, Any]) -> None:
        await AsyncHttpUtil.head("https://example.com/")
        assert mock_async["calls"][0].method == "HEAD"

    @pytest.mark.asyncio
    async def test_options(self, mock_async: dict[str, Any]) -> None:
        await AsyncHttpUtil.options("https://example.com/")
        assert mock_async["calls"][0].method == "OPTIONS"

    @pytest.mark.asyncio
    async def test_get_with_params_headers(self, mock_async: dict[str, Any]) -> None:
        await AsyncHttpUtil.get(
            "https://example.com/",
            params={"q": "h"},
            headers={"X-Token": "tok"},
        )
        call = mock_async["calls"][0]
        assert "q=h" in str(call.url)
        assert call.headers["X-Token"] == "tok"


# ---------------------------------------------------------------------
# 下载测试
# ---------------------------------------------------------------------
class TestDownload:
    """文件下载。"""

    def test_sync_download(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        # 自定义 transport 返回固定内容
        payload = b"hello world" * 100

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, content=payload)

        transport = MockTransport(handler)
        original_client = httpx.Client

        def patched_client(*args: Any, **kwargs: Any) -> Any:
            kwargs.setdefault("transport", transport)
            return original_client(*args, **kwargs)

        monkeypatch.setattr(httpx, "Client", patched_client)

        dest = tmp_path / "out" / "file.bin"
        result = HttpUtil.download("https://example.com/file", dest)
        assert result == dest
        assert dest.exists()
        assert dest.read_bytes() == payload

    @pytest.mark.asyncio
    async def test_async_download(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        payload = b"hello world" * 100

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, content=payload)

        transport = MockTransport(handler)
        original_client = httpx.AsyncClient

        def patched_client(*args: Any, **kwargs: Any) -> Any:
            kwargs.setdefault("transport", transport)
            return original_client(*args, **kwargs)

        monkeypatch.setattr(httpx, "AsyncClient", patched_client)

        dest = tmp_path / "out" / "file.bin"
        result = await AsyncHttpUtil.download("https://example.com/file", dest)
        assert result == dest
        assert dest.exists()
        assert dest.read_bytes() == payload


# ---------------------------------------------------------------------
# 缺失依赖测试
# ---------------------------------------------------------------------
class TestMissingDependency:
    """模拟 httpx 未安装场景。"""

    def test_get_without_httpx_raises_util_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        import pyhutool.http.http_util as mod

        def _raise() -> Any:
            raise UtilError(
                "pyhutool.http 需要 httpx 支持，请运行：pip install 'pyhutool[http]'",
                cause=ImportError("simulated: httpx not installed"),
            )

        monkeypatch.setattr(mod, "_require_httpx", _raise)
        with pytest.raises(UtilError) as excinfo:
            HttpUtil.get("https://example.com/")
        assert "pyhutool[http]" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_async_get_without_httpx_raises_util_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        import pyhutool.http.http_util as mod

        def _raise() -> Any:
            raise UtilError(
                "pyhutool.http 需要 httpx 支持，请运行：pip install 'pyhutool[http]'",
                cause=ImportError("simulated: httpx not installed"),
            )

        monkeypatch.setattr(mod, "_require_httpx", _raise)
        with pytest.raises(UtilError) as excinfo:
            await AsyncHttpUtil.get("https://example.com/")
        assert "pyhutool[http]" in str(excinfo.value)
