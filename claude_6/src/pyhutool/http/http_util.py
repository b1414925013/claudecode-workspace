"""HTTP 客户端工具。

对齐 Hutool 的 ``cn.hutool.http.HttpUtil`` 与 ``HttpRequest``/``HttpResponse``，
基于 ``httpx`` 提供同步与异步双套 API。

设计说明
--------
- ``httpx`` 是可选依赖；未安装时调用任何方法抛 ``UtilError``；
- 同步版 ``HttpUtil`` 基于 ``httpx.Client``，每次请求使用 ``with`` 上下文
  管理确保连接释放；
- 异步版 ``AsyncHttpUtil`` 基于 ``httpx.AsyncClient``，方法均为协程；
- ``HttpResponse`` 包装 ``httpx.Response``，提供与 Hutool ``HttpResponse``
  风格一致的方法名（``body`` / ``body_bytes`` / ``is_ok`` 等）；
- 默认超时 30s，可通过 ``timeout`` 参数覆盖。
"""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Final, cast

from pyhutool.core.exceptions import UtilError

__all__ = ["AsyncHttpUtil", "HttpResponse", "HttpUtil"]

_DEFAULT_TIMEOUT: Final[float] = 30.0
_DEFAULT_USER_AGENT: Final[str] = "pyhutool/0.1.0"


def _require_httpx() -> Any:
    """惰性导入 ``httpx``；未安装时抛 ``UtilError``。"""
    try:
        import httpx
    except ImportError as e:
        raise UtilError(
            "pyhutool.http 需要 httpx 支持，请运行：pip install 'pyhutool[http]'",
            cause=e,
        ) from e
    return httpx


class HttpResponse:
    """HTTP 响应包装类。

    包装 ``httpx.Response``，提供 Hutool 风格的方法名。

    Parameters
    ----------
    raw:
        底层 ``httpx.Response`` 对象。
    """

    def __init__(self, raw: Any) -> None:
        """初始化响应包装。"""
        self._raw = raw

    # ------------------------------------------------------------------
    # 状态
    # ------------------------------------------------------------------
    @property
    def status(self) -> int:
        """HTTP 状态码。"""
        return int(self._raw.status_code)

    @property
    def status_code(self) -> int:
        """HTTP 状态码（``httpx`` 习惯命名）。"""
        return int(self._raw.status_code)

    @property
    def is_success(self) -> bool:
        """是否 2xx。"""
        return bool(200 <= int(self._raw.status_code) < 300)

    @property
    def is_ok(self) -> bool:
        """是否 2xx（Hutool 风格别名）。"""
        return self.is_success

    @property
    def is_redirect(self) -> bool:
        """是否 3xx 重定向。"""
        return bool(300 <= int(self._raw.status_code) < 400)

    @property
    def is_client_error(self) -> bool:
        """是否 4xx。"""
        return bool(400 <= int(self._raw.status_code) < 500)

    @property
    def is_server_error(self) -> bool:
        """是否 5xx。"""
        return bool(500 <= int(self._raw.status_code) < 600)

    # ------------------------------------------------------------------
    # 头部
    # ------------------------------------------------------------------
    @property
    def headers(self) -> Mapping[str, str]:
        """响应头映射（大小写不敏感，直接返回 ``httpx.Headers``）。"""
        # 直接返回原生 Headers 对象，避免 ``dict(headers)`` 把 key 规范化为
        # 小写后导致大小写敏感访问失败。
        return cast("Mapping[str, str]", self._raw.headers)

    def header(self, name: str, default: str | None = None) -> str | None:
        """获取单个响应头（大小写不敏感）。"""
        value = self._raw.headers.get(name, default)
        return cast("str | None", value)

    @property
    def content_type(self) -> str | None:
        """``Content-Type`` 响应头。"""
        return self.header("Content-Type")

    # ------------------------------------------------------------------
    # 主体
    # ------------------------------------------------------------------
    @property
    def text(self) -> str:
        """响应体文本（自动按 charset 解码）。"""
        return cast(str, self._raw.text)

    @property
    def body(self) -> str:
        """响应体文本（Hutool 风格别名）。"""
        return self.text

    @property
    def content(self) -> bytes:
        """响应体原始字节。"""
        return cast(bytes, self._raw.content)

    @property
    def body_bytes(self) -> bytes:
        """响应体原始字节（Hutool 风格别名）。"""
        return self.content

    def json(self) -> Any:
        """把响应体解析为 JSON 对象。

        委托给 ``pyhutool.json.JsonUtil.parse`` 以保持统一异常类型。
        """
        from pyhutool.json import JsonUtil

        return JsonUtil.parse(self.content)

    # ------------------------------------------------------------------
    # 其他
    # ------------------------------------------------------------------
    @property
    def url(self) -> str:
        """最终响应 URL（重定向后）。"""
        return str(self._raw.url)

    @property
    def encoding(self) -> str | None:
        """响应解码字符集。"""
        return cast("str | None", self._raw.encoding)

    def raise_for_status(self) -> None:
        """状态码 4xx/5xx 抛 ``UtilError``。"""
        if self._raw.status_code >= 400:
            raise UtilError(
                f"HTTP {self._raw.status_code}: {self._raw.reason_phrase}",
            )

    def __repr__(self) -> str:
        """返回响应可打印表示。"""
        return f"<HttpResponse [{self.status}]>"


def _build_headers(
    headers: Mapping[str, str] | None,
    user_agent: str | None,
) -> dict[str, str]:
    """合并默认 UA 与用户传入的 headers。"""
    result: dict[str, str] = {}
    if user_agent is not None:
        result["User-Agent"] = user_agent
    if headers:
        result.update(headers)
    return result


def _request_kwargs(
    params: Mapping[str, str] | None,
    headers: Mapping[str, str] | None,
    auth: tuple[str, str] | None,
    timeout: float | None,
    follow_redirects: bool,
) -> dict[str, Any]:
    """把可选参数组装成 ``httpx.Client.request`` 接受的 kwargs。

    说明：``cookies`` 不在此处处理，而是直接传给 ``Client`` 构造函数，
    避免 ``httpx`` 对 per-request ``cookies=...`` 的 ``DeprecationWarning``。
    """
    kwargs: dict[str, Any] = {
        "params": dict(params) if params else None,
        "headers": dict(headers) if headers else None,
        "auth": auth,
        "timeout": timeout if timeout is not None else _DEFAULT_TIMEOUT,
        "follow_redirects": follow_redirects,
    }
    return kwargs


def _client_kwargs(cookies: Mapping[str, str] | None) -> dict[str, Any]:
    """构造 ``httpx.Client`` 初始化 kwargs（仅 cookies）。"""
    if cookies is None:
        return {}
    return {"cookies": dict(cookies)}


class HttpUtil:
    """同步 HTTP 客户端工具，全部为静态方法。

    对应 Hutool ``cn.hutool.http.HttpUtil``。每次请求都会创建一个新的
    ``httpx.Client``，调用完毕即关闭；适合一次性调用场景。如需连接复用，
    请直接使用 ``httpx.Client``。
    """

    # ------------------------------------------------------------------
    # 通用请求
    # ------------------------------------------------------------------
    @staticmethod
    def request(
        method: str,
        url: str,
        *,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | None = None,
        follow_redirects: bool = True,
        data: Any = None,
        json: Any = None,
        files: Mapping[str, Any] | None = None,
        content: bytes | str | None = None,
        user_agent: str | None = _DEFAULT_USER_AGENT,
    ) -> HttpResponse:
        """发起 HTTP 请求。

        Parameters
        ----------
        method:
            HTTP 方法（``GET``/``POST``/...）。
        url:
            目标 URL。
        params:
            查询参数。
        headers:
            自定义请求头。
        cookies:
            Cookie。
        auth:
            ``Basic Auth`` 元组 ``(user, password)``。
        timeout:
            超时秒数，默认 30s。
        follow_redirects:
            是否跟随重定向。
        data:
            表单数据（``dict`` 或字节）。
        json:
            JSON 体（任意可序列化对象，将自动 ``json.dumps``）。
        files:
            文件上传（``{field: (name, file_obj)}``）。
        content:
            原始请求体（字节或字符串）。
        user_agent:
            ``User-Agent`` 头。``None`` 不设置；默认 ``pyhutool/0.1.0``。
        """
        httpx = _require_httpx()
        final_headers = _build_headers(headers, user_agent)
        kwargs = _request_kwargs(
            params, final_headers, auth, timeout, follow_redirects
        )
        # 请求体参数：data / json / files / content 互斥
        kwargs["data"] = data
        kwargs["json"] = json
        kwargs["files"] = files
        kwargs["content"] = content
        # 清掉 None 值避免 httpx 警告
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        try:
            with httpx.Client(**_client_kwargs(cookies)) as client:
                raw = client.request(method.upper(), url, **kwargs)
        except httpx.HTTPError as e:
            raise UtilError(f"HTTP 请求失败: {e}", cause=e) from e
        return HttpResponse(raw)

    # ------------------------------------------------------------------
    # 便捷方法
    # ------------------------------------------------------------------
    @staticmethod
    def get(
        url: str,
        *,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | None = None,
        follow_redirects: bool = True,
        user_agent: str | None = _DEFAULT_USER_AGENT,
    ) -> HttpResponse:
        """发起 GET 请求。"""
        return HttpUtil.request(
            "GET",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
            user_agent=user_agent,
        )

    @staticmethod
    def post(
        url: str,
        *,
        data: Any = None,
        json: Any = None,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | None = None,
        follow_redirects: bool = True,
        files: Mapping[str, Any] | None = None,
        content: bytes | str | None = None,
        user_agent: str | None = _DEFAULT_USER_AGENT,
    ) -> HttpResponse:
        """发起 POST 请求。"""
        return HttpUtil.request(
            "POST",
            url,
            data=data,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
            files=files,
            content=content,
            user_agent=user_agent,
        )

    @staticmethod
    def put(
        url: str,
        *,
        data: Any = None,
        json: Any = None,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | None = None,
        follow_redirects: bool = True,
        content: bytes | str | None = None,
        user_agent: str | None = _DEFAULT_USER_AGENT,
    ) -> HttpResponse:
        """发起 PUT 请求。"""
        return HttpUtil.request(
            "PUT",
            url,
            data=data,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
            content=content,
            user_agent=user_agent,
        )

    @staticmethod
    def delete(
        url: str,
        *,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | None = None,
        follow_redirects: bool = True,
        user_agent: str | None = _DEFAULT_USER_AGENT,
    ) -> HttpResponse:
        """发起 DELETE 请求。"""
        return HttpUtil.request(
            "DELETE",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
            user_agent=user_agent,
        )

    @staticmethod
    def patch(
        url: str,
        *,
        data: Any = None,
        json: Any = None,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | None = None,
        follow_redirects: bool = True,
        content: bytes | str | None = None,
        user_agent: str | None = _DEFAULT_USER_AGENT,
    ) -> HttpResponse:
        """发起 PATCH 请求。"""
        return HttpUtil.request(
            "PATCH",
            url,
            data=data,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
            content=content,
            user_agent=user_agent,
        )

    @staticmethod
    def head(
        url: str,
        *,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | None = None,
        follow_redirects: bool = True,
        user_agent: str | None = _DEFAULT_USER_AGENT,
    ) -> HttpResponse:
        """发起 HEAD 请求。"""
        return HttpUtil.request(
            "HEAD",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
            user_agent=user_agent,
        )

    @staticmethod
    def options(
        url: str,
        *,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | None = None,
        follow_redirects: bool = True,
        user_agent: str | None = _DEFAULT_USER_AGENT,
    ) -> HttpResponse:
        """发起 OPTIONS 请求。"""
        return HttpUtil.request(
            "OPTIONS",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
            user_agent=user_agent,
        )

    # ------------------------------------------------------------------
    # 文件下载
    # ------------------------------------------------------------------
    @staticmethod
    def download(
        url: str,
        dest: str | Path,
        *,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | None = None,
        follow_redirects: bool = True,
        chunk_size: int = 8192,
        user_agent: str | None = _DEFAULT_USER_AGENT,
    ) -> Path:
        """下载 URL 内容到本地文件，返回目标文件 ``Path``。

        对应 Hutool ``HttpUtil.downloadFile``。
        """
        httpx = _require_httpx()
        final_headers = _build_headers(headers, user_agent)
        kwargs = _request_kwargs(
            params, final_headers, auth, timeout, follow_redirects
        )
        dest_path = Path(dest)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # 直接通过 ``Client().stream(...)`` 发起流式请求，便于测试
            # 通过 monkeypatch ``httpx.Client`` 注入 MockTransport。
            with httpx.Client(**_client_kwargs(cookies)) as client, client.stream(
                "GET", url, **kwargs
            ) as resp:
                resp.raise_for_status()
                with dest_path.open("wb") as f:
                    for chunk in resp.iter_bytes(chunk_size):
                        if chunk:
                            f.write(chunk)
        except httpx.HTTPError as e:
            raise UtilError(f"下载失败: {url}", cause=e) from e
        return dest_path


class AsyncHttpUtil:
    """异步 HTTP 客户端工具。

    每个方法对应 ``HttpUtil`` 同名方法，但返回协程。基于
    ``httpx.AsyncClient``。
    """

    # ------------------------------------------------------------------
    # 通用请求
    # ------------------------------------------------------------------
    @staticmethod
    async def request(
        method: str,
        url: str,
        *,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | None = None,
        follow_redirects: bool = True,
        data: Any = None,
        json: Any = None,
        files: Mapping[str, Any] | None = None,
        content: bytes | str | None = None,
        user_agent: str | None = _DEFAULT_USER_AGENT,
    ) -> HttpResponse:
        """异步发起 HTTP 请求。"""
        httpx = _require_httpx()
        final_headers = _build_headers(headers, user_agent)
        kwargs = _request_kwargs(
            params, final_headers, auth, timeout, follow_redirects
        )
        kwargs["data"] = data
        kwargs["json"] = json
        kwargs["files"] = files
        kwargs["content"] = content
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        try:
            async with httpx.AsyncClient(**_client_kwargs(cookies)) as client:
                raw = await client.request(method.upper(), url, **kwargs)
        except httpx.HTTPError as e:
            raise UtilError(f"HTTP 请求失败: {e}", cause=e) from e
        return HttpResponse(raw)

    # ------------------------------------------------------------------
    # 便捷方法
    # ------------------------------------------------------------------
    @staticmethod
    async def get(
        url: str,
        *,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | None = None,
        follow_redirects: bool = True,
        user_agent: str | None = _DEFAULT_USER_AGENT,
    ) -> HttpResponse:
        """异步发起 GET 请求。"""
        return await AsyncHttpUtil.request(
            "GET",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
            user_agent=user_agent,
        )

    @staticmethod
    async def post(
        url: str,
        *,
        data: Any = None,
        json: Any = None,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | None = None,
        follow_redirects: bool = True,
        files: Mapping[str, Any] | None = None,
        content: bytes | str | None = None,
        user_agent: str | None = _DEFAULT_USER_AGENT,
    ) -> HttpResponse:
        """异步发起 POST 请求。"""
        return await AsyncHttpUtil.request(
            "POST",
            url,
            data=data,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
            files=files,
            content=content,
            user_agent=user_agent,
        )

    @staticmethod
    async def put(
        url: str,
        *,
        data: Any = None,
        json: Any = None,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | None = None,
        follow_redirects: bool = True,
        content: bytes | str | None = None,
        user_agent: str | None = _DEFAULT_USER_AGENT,
    ) -> HttpResponse:
        """异步发起 PUT 请求。"""
        return await AsyncHttpUtil.request(
            "PUT",
            url,
            data=data,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
            content=content,
            user_agent=user_agent,
        )

    @staticmethod
    async def delete(
        url: str,
        *,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | None = None,
        follow_redirects: bool = True,
        user_agent: str | None = _DEFAULT_USER_AGENT,
    ) -> HttpResponse:
        """异步发起 DELETE 请求。"""
        return await AsyncHttpUtil.request(
            "DELETE",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
            user_agent=user_agent,
        )

    @staticmethod
    async def patch(
        url: str,
        *,
        data: Any = None,
        json: Any = None,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | None = None,
        follow_redirects: bool = True,
        content: bytes | str | None = None,
        user_agent: str | None = _DEFAULT_USER_AGENT,
    ) -> HttpResponse:
        """异步发起 PATCH 请求。"""
        return await AsyncHttpUtil.request(
            "PATCH",
            url,
            data=data,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
            content=content,
            user_agent=user_agent,
        )

    @staticmethod
    async def head(
        url: str,
        *,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | None = None,
        follow_redirects: bool = True,
        user_agent: str | None = _DEFAULT_USER_AGENT,
    ) -> HttpResponse:
        """异步发起 HEAD 请求。"""
        return await AsyncHttpUtil.request(
            "HEAD",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
            user_agent=user_agent,
        )

    @staticmethod
    async def options(
        url: str,
        *,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | None = None,
        follow_redirects: bool = True,
        user_agent: str | None = _DEFAULT_USER_AGENT,
    ) -> HttpResponse:
        """异步发起 OPTIONS 请求。"""
        return await AsyncHttpUtil.request(
            "OPTIONS",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
            user_agent=user_agent,
        )

    # ------------------------------------------------------------------
    # 文件下载
    # ------------------------------------------------------------------
    @staticmethod
    async def download(
        url: str,
        dest: str | Path,
        *,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | None = None,
        follow_redirects: bool = True,
        chunk_size: int = 8192,
        user_agent: str | None = _DEFAULT_USER_AGENT,
    ) -> Path:
        """异步下载文件。"""
        httpx = _require_httpx()
        final_headers = _build_headers(headers, user_agent)
        kwargs = _request_kwargs(
            params, final_headers, auth, timeout, follow_redirects
        )
        dest_path = Path(dest)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            async with httpx.AsyncClient(**_client_kwargs(cookies)) as client, client.stream(
                "GET", url, **kwargs
            ) as resp:
                resp.raise_for_status()
                # 流式写入委托给线程池避免阻塞事件循环
                f = await asyncio.to_thread(dest_path.open, "wb")
                try:
                    async for chunk in resp.aiter_bytes(chunk_size):
                        if chunk:
                            await asyncio.to_thread(f.write, chunk)
                finally:
                    await asyncio.to_thread(f.close)
        except httpx.HTTPError as e:
            raise UtilError(f"下载失败: {url}", cause=e) from e
        return dest_path
