---
name: api-investigator
description: API 调查助手。使用 Playwright 捕获并分析 HTTP 流量，解明 API 行为。
allowed-tools: Read Edit Write Glob Grep Bash
---

# API 调查助手

此技能提供使用 Playwright 调查任意网站 API 行为的方法。

## 何时使用此技能

1. **API 行为调查时**：需要确认目标网站的 API 请求/响应格式
2. **新功能实现前的调查**：需要了解未知 API 端点行为时
3. **Bug 调查时**：诊断 API 通信相关问题
4. **爬虫开发时**：分析目标网站的 API 结构
5. **认证流程分析**：了解登录/会话管理机制

## 前置条件

### 必需软件

- Playwright（`pip install playwright`）
- Playwright 浏览器（`playwright install chromium`）

### 可选软件

- mitmproxy（仅当你需要解密第三方 HTTPS 流量时才需要）

## 核心方法：Playwright 网络监听

```python
from playwright.sync_api import sync_playwright
import json

api_requests = []

def handle_request(request):
    """记录每个请求"""
    entry = {
        'method': request.method,
        'url': request.url,
        'headers': dict(request.headers),
    }
    # 记录请求体
    try:
        if hasattr(request, 'post_data_buffer') and request.post_data_buffer:
            entry['body'] = request.post_data_buffer.decode('utf-8', errors='ignore')
    except:
        pass
    api_requests.append(entry)

def handle_response(response):
    """记录每个响应"""
    for entry in api_requests:
        if entry['url'] == response.url and entry['method'] == response.request.method:
            entry['status_code'] = response.status
            entry['response_headers'] = dict(response.headers)
            if response.body:
                try:
                    entry['response_body'] = response.body[:50000].decode('utf-8', errors='ignore')
                except:
                    pass
            break

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 设置监听
        page.on('request', handle_request)
        page.on('response', handle_response)

        # 导航到目标网站
        page.goto("https://target-site.com/", wait_until="load")

        # 执行操作（点击、输入等）
        # ...

        browser.close()

    # 保存结果
    with open('api_log.json', 'w', encoding='utf-8') as f:
        json.dump(api_requests, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
```

## 常用代码模板

### 模板 1：基础 API 抓取

```python
from playwright.sync_api import sync_playwright
import json
import time
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

api_requests = []

def handle_request(request):
    entry = {
        'method': request.method,
        'url': request.url,
        'headers': dict(request.headers),
    }
    try:
        if hasattr(request, 'post_data_buffer') and request.post_data_buffer:
            entry['body'] = request.post_data_buffer.decode('utf-8', errors='ignore')
    except:
        pass
    api_requests.append(entry)
    # 过滤静态资源
    if not any(ext in request.url for ext in ['.css', '.js', '.png', '.jpg', '.jpeg', '.woff', '.webp', '.gif']):
        print(f"[API] {request.method} {request.url}")

def handle_response(response):
    for entry in api_requests:
        if entry['url'] == response.url and entry['method'] == response.request.method:
            entry['status_code'] = response.status
            entry['response_headers'] = dict(response.headers)
            if response.body:
                try:
                    entry['response_body'] = response.body[:50000].decode('utf-8', errors='ignore')
                except:
                    pass
            break

def close_popup(page):
    """关闭常见弹窗"""
    selectors = ['.close', '[data-dismiss]', '.popup button', '.modal-close', 'button.close']
    for selector in selectors:
        try:
            page.locator(selector).first.click(timeout=500)
            return True
        except:
            pass
    return False

def click_element(page, text, exact=False):
    """点击包含文本的元素"""
    selectors = [
        f'a:has-text("{text}")',
        f'button:has-text("{text}")',
        f'[role="button"]:has-text("{text}")',
    ]
    for selector in selectors:
        try:
            page.locator(selector).first.click(timeout=3000)
            return True
        except:
            pass
    return False

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.on('request', handle_request)
        page.on('response', handle_response)

        # 1. 打开网站
        page.goto("https://target-site.com/", wait_until="load", timeout=60000)
        time.sleep(2)

        # 2. 关闭弹窗（如有）
        close_popup(page)

        # 3. 执行操作
        click_element(page, "目标按钮")

        time.sleep(2)
        browser.close()

    # 保存
    with open('api_log.json', 'w', encoding='utf-8') as f:
        json.dump(api_requests, f, ensure_ascii=False, indent=2)
    print(f"已保存 {len(api_requests)} 条 API")

if __name__ == '__main__':
    main()
```

### 模板 2：导出 Postman 集合

```python
import json
from urllib.parse import urlparse

def export_postman(api_requests, output_file='postman_collection.json'):
    """将 API 日志导出为 Postman 集合格式"""
    collection = {
        "info": {
            "name": "API 集合",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": []
    }

    # 按域名分组
    url_groups = {}
    for entry in api_requests:
        parsed = urlparse(entry.get('url', ''))
        host = parsed.netloc or 'unknown'
        if host not in url_groups:
            url_groups[host] = []
        url_groups[host].append(entry)

    for host, entries in url_groups.items():
        folder = {"name": host, "item": []}
        for entry in entries:
            request = {
                "name": entry.get('url', ''),
                "request": {
                    "method": entry.get('method', 'GET'),
                    "url": {"raw": entry.get('url', ''), "protocol": "https"},
                    "header": [{"key": k, "value": v} for k, v in entry.get('headers', {}).items()]
                }
            }
            if entry.get('body'):
                request["request"]["body"] = {"mode": "raw", "raw": entry['body']}
            folder["item"].append(request)
        collection["item"].append(folder)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(collection, f, ensure_ascii=False, indent=2)

    return len(api_requests)
```

## 调查工作流程

### 步骤 1：分析首页 API

1. 打开网站首页，观察发出的 API 请求
2. 记录关键 API 端点（登录、列表、详情等）

### 步骤 2：导航到目标页面

1. 点击功能按钮（如"网游单机"）
2. 观察新产生的 API 请求
3. 分析分页参数、筛选条件

### 步骤 3：导出并分析

```python
# 分析特定模式的 API
pattern = "api"  # 替换为你要搜索的关键词
matching = [r for r in api_requests if pattern.lower() in r['url'].lower()]
print(f"找到 {len(matching)} 条匹配")

# 查找 POST 请求
posts = [r for r in api_requests if r['method'] == 'POST']
for p in posts:
    print(f"POST: {p['url']}")
```

## 常见问题调试

### 元素被弹窗遮挡

```python
# 先关闭弹窗
close_popup(page)

# 再执行点击
page.get_by_text("目标文本").click()
```

### 点击没反应

```python
# 使用 force=True 强制点击
page.locator('selector').click(force=True)

# 或使用 JavaScript 直接点击
page.evaluate('document.querySelector("selector").click()')
```

### 网络超时

```python
page.goto(url, wait_until="load", timeout=120000)  # 增加超时时间
```

### 需要监听特定域名

```python
def handle_request(request):
    if 'api.target-site.com' in request.url:  # 过滤特定域名
        api_requests.append({...})
```

## mitmproxy 使用场景（可选）

仅当你需要**解密第三方 HTTPS 流量**时才需要 mitmproxy，例如：
- 第三方广告 SDK 的请求
- 第三方分析服务的请求
- 无法直接从 Playwright 观察到的 iframe 请求

### mitmproxy 启动方式

```bash
# Windows
mitmdump --listen-port 8080 -w traffic.flow

# 然后配置浏览器代理或使用 Playwright 代理模式
```

### Playwright 使用代理

```python
browser = p.chromium.launch(proxy={"server": "http://127.0.0.1:8080"})
```

## 输出文件

| 文件 | 说明 |
|------|------|
| `api_log.json` | 完整 API 日志（请求+响应） |
| `postman_collection.json` | Postman 集合格式，可直接导入 |
| `step*.png` | 关键步骤截图，便于调试 |

## 注意事项

- 捕获数据可能包含会话信息，分享时请注意脱敏
- 请遵守目标网站的服务条款
- 仅限开发/调查目的使用