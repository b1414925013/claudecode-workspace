"""pyhutool.http - HTTP 客户端模块（依赖 httpx）。

对齐 Hutool 的 ``cn.hutool.http.HttpUtil`` 与 ``cn.hutool.http.HttpRequest``/
``HttpResponse``，提供同步与异步双套 API。

模块概览：
    - ``HttpUtil``         同步 HTTP 客户端，基于 ``httpx.Client``
    - ``AsyncHttpUtil``    异步 HTTP 客户端，基于 ``httpx.AsyncClient``
    - ``HttpResponse``     响应包装类（同步/异步通用）

依赖说明
--------
``httpx`` 是可选依赖。未安装时调用任何方法都会抛 ``UtilError``，提示
``pip install "pyhutool[http]"``。
"""

from pyhutool.http.http_util import AsyncHttpUtil, HttpResponse, HttpUtil

__all__ = ["AsyncHttpUtil", "HttpResponse", "HttpUtil"]
