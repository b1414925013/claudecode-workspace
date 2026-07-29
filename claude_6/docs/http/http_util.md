# HttpUtil HTTP 客户端

`pyhutool.http.HttpUtil` / `AsyncHttpUtil` 对齐 Hutool `cn.hutool.http.HttpUtil`，
基于 [httpx](https://www.python-httpx.org/) 提供同步与异步双套 API。

## 安装

```bash
pip install "pyhutool[http]"
```

未安装 ``httpx`` 时调用任何方法都会抛 ``UtilError``。

## 快速开始

```python
from pyhutool.http import HttpUtil, AsyncHttpUtil

# 同步
resp = HttpUtil.get("https://httpbin.org/get", params={"q": "pyhutool"})
print(resp.status, resp.text)

# 异步
async def main() -> None:
    resp = await AsyncHttpUtil.get("https://httpbin.org/get")
    print(resp.status, resp.text)
```

## 请求方法

```python
HttpUtil.get(url, params=..., headers=..., auth=("user", "pwd"), timeout=10)
HttpUtil.post(url, json={"k": "v"})
HttpUtil.post(url, data={"k": "v"})               # 表单
HttpUtil.post(url, content=b"raw bytes")          # 原始字节
HttpUtil.post(url, files={"f": ("a.txt", fp)})     # 文件上传
HttpUtil.put(url, json={...})
HttpUtil.patch(url, json={...})
HttpUtil.delete(url)
HttpUtil.head(url)
HttpUtil.options(url)

# 通用方法
HttpUtil.request("GET", url, ...)
```

默认 ``User-Agent: pyhutool/0.1.0``，可通过 ``user_agent=None`` 关闭或自定义。

## 响应

```python
resp = HttpUtil.get("https://httpbin.org/json")

resp.status                    # 200
resp.status_code               # 同上（httpx 风格）
resp.is_success                # 2xx
resp.is_ok                     # 同上（Hutool 风格）
resp.is_redirect               # 3xx
resp.is_client_error           # 4xx
resp.is_server_error           # 5xx

resp.text                      # 解码后字符串
resp.body                      # 同上（Hutool 风格）
resp.content                   # 原始字节
resp.body_bytes                # 同上（Hutool 风格）
resp.headers                    # dict[str, str]
resp.header("Content-Type")
resp.content_type
resp.url                       # 最终 URL（重定向后）
resp.encoding

resp.json()                    # 解析 JSON（委托 JsonUtil）

resp.raise_for_status()        # 4xx/5xx 抛 UtilError
repr(resp)                     # <HttpResponse [200]>
```

## 文件下载

```python
# 同步
dest = HttpUtil.download("https://example.com/file.zip", "downloads/file.zip")

# 异步
dest = await AsyncHttpUtil.download("https://example.com/file.zip", "downloads/file.zip")
```

下载使用流式写入，避免大文件占用内存；自动创建父目录。

## 异步版完整 API

```python
await AsyncHttpUtil.get(url, ...)
await AsyncHttpUtil.post(url, ...)
await AsyncHttpUtil.put(url, ...)
await AsyncHttpUtil.patch(url, ...)
await AsyncHttpUtil.delete(url)
await AsyncHttpUtil.head(url)
await AsyncHttpUtil.options(url)
await AsyncHttpUtil.request(method, url, ...)
await AsyncHttpUtil.download(url, dest)
```

## 与 Hutool 的差异

| 方面 | Hutool (Java) | pyhutool (Python) |
|------|---------------|-------------------|
| 客户端 | ``java.net.HttpURLConnection`` | ``httpx`` |
| 异步 | 不支持 | 双套 sync + async |
| 响应 | ``HttpResponse`` 包装类 | ``HttpResponse`` 包装类（同风格） |
| 文件上传 | ``form(...)`` | ``files={field: (name, fp)}`` |
| 异常 | ``IORuntimeException`` | ``UtilError`` |
| 依赖 | 内置 | ``httpx`` (extras) |
