---
name: playwright-cli
description: 使用微软 playwright-cli 命令行进行浏览器自动化：打开网页、点击、填表、截图、抓取、网络拦截、多会话管理。当用户要求用 playwright-cli 操作浏览器、进行网页自动化/测试/数据抓取/截图时调用本 skill。
---

# Playwright CLI 浏览器自动化指南

`playwright-cli`（npm 包名 `@playwright/cli`）是微软 2026 年初开源的浏览器自动化命令行工具，专为 AI 编码代理设计。相比 Playwright MCP，它把页面快照/截图写到磁盘而不是塞进模型上下文，官方基准测试 token 消耗约少 4.6 倍。

**工作原理**：客户端-守护进程（client-daemon）架构。每条命令通过本地 socket 发给后台 daemon，浏览器常驻不重启；每次操作后自动生成新的无障碍快照（YAML）写入工作区 `.playwright-cli/` 目录，命令输出只返回一个文件路径，按需读取。

---

## 1. 安装与初始化

```powershell
# 全局安装（需要 Node.js 18+）
npm install -g @playwright/cli@latest

# 验证
playwright-cli --version

# 安装浏览器二进制（系统已装 Chrome 时默认直接用 Chrome，可跳过）
playwright-cli install-browser                          # Chromium
playwright-cli install-browser --browser=firefox
playwright-cli install-browser --browser=webkit
```

若全局命令不存在，先检查项目本地版本：`npx --no-install playwright --version`，可用则所有命令改为 `npx playwright cli <command>`。

---

## 2. 最小工作流（核心心智模型）

```powershell
playwright-cli open https://example.com --headed   # 打开浏览器（--headed 有界面，默认无头）
playwright-cli snapshot                            # 获取快照，得到元素引用（如 e15）
playwright-cli fill e5 "user@example.com"          # 用 ref 操作元素
playwright-cli click e3                            # 点击
playwright-cli close                               # 结束后关闭
```

**关键规则**：
- 所有交互都基于**最新快照中的 ref**（如 `e15`）。页面变化后旧 ref 可能失效，需重新 `snapshot`。
- 每条命令执行后 CLI 自动返回新快照文件路径（如 `.playwright-cli/page-2026-xx-xx.yml`），**用 Read 工具按需读取该文件**，不要盲目全量读取。
- 截图同样写磁盘返回路径，用 Read 工具读图查看。

---

## 3. 命令速查表

### 3.1 打开与导航

```powershell
playwright-cli open                                  # 空白页启动
playwright-cli open https://example.com/             # 启动并直接导航
playwright-cli open https://example.com --headed     # 有头模式（调试推荐）
playwright-cli open --browser=chrome                 # 指定浏览器: chrome/firefox/webkit/msedge
playwright-cli open --mobile                         # 移动端模拟（快照更小更省 token）
playwright-cli open --device="iPhone 15"             # 指定设备模拟
playwright-cli open --persistent                     # 持久化用户目录（保留登录态/cookie）
playwright-cli open --profile=D:\path\to\profile     # 指定持久化目录
playwright-cli goto https://example.com              # 当前页导航
playwright-cli go-back / go-forward / reload
playwright-cli resize 1920 1080
playwright-cli close                                 # 关闭当前会话浏览器
```

### 3.2 交互

```powershell
playwright-cli click e3                              # 单击
playwright-cli dblclick e7                           # 双击
playwright-cli fill e5 "user@example.com" --submit   # 填充并回车提交
playwright-cli type "search query"                   # 向焦点元素打字（逐键，触发键盘事件）
playwright-cli hover e4                              # 悬停（可触发下拉菜单）
playwright-cli select e9 "option-value"              # 下拉框选择
playwright-cli check e12 / uncheck e12               # 勾选/取消复选框
playwright-cli drag e2 e8                            # 两个元素间拖拽
playwright-cli drop e4 --path=./image.png            # 向页面元素投放本地文件
playwright-cli drop e4 --data="text/plain=hello"     # 投放文本数据
playwright-cli upload ./document.pdf                 # 上传文件到文件选择控件
```

### 3.3 键盘与鼠标（坐标级操作）

```powershell
playwright-cli press Enter                           # 回车/Tab/ArrowDown 等
playwright-cli keydown Shift / keyup Shift
playwright-cli mousemove 150 300                     # 移动到坐标
playwright-cli mousedown / mouseup                   # 左键按下/抬起
playwright-cli mousedown right / mouseup right       # 右键
playwright-cli mousewheel 0 100                      # 滚动
```

### 3.4 快照、截图与状态

```powershell
playwright-cli snapshot                              # 全页快照（YAML + refs）
playwright-cli snapshot --filename=after-click.yaml  # 指定文件名
playwright-cli snapshot "#main"                      # 只快照某元素
playwright-cli snapshot --depth=4                    # 限制深度，先概览再深入（省 token）
playwright-cli snapshot --boxes                      # 附带元素包围盒 [box=x,y,w,h]
playwright-cli find "Sign in"                        # 在快照中搜索文本，返回匹配节点+上下文
playwright-cli find --regex "/sign (in|up)/i"        # 正则搜索（/…/i 加 flag）
playwright-cli screenshot                            # 截图（写磁盘）
playwright-cli screenshot e5                         # 截取单个元素
playwright-cli screenshot --hires                    # 高清截图
playwright-cli pdf --filename=page.pdf               # 导出 PDF
playwright-cli eval "document.title"                 # 执行 JS 表达式
playwright-cli eval "el => el.textContent" e5        # 对某元素执行 JS
playwright-cli eval "el => el.getAttribute('data-testid')" e5   # 读取快照中不可见的属性
```

### 3.5 多标签页

```powershell
playwright-cli tab-list                              # 列出标签页
playwright-cli tab-new https://example.com           # 新建标签页
playwright-cli tab-select 0                          # 切换标签页
playwright-cli tab-close 2                           # 关闭指定标签页
```

### 3.6 登录态与存储

```powershell
playwright-cli state-save auth.json                  # 导出 cookie+storage
playwright-cli state-load auth.json                  # 恢复登录态
playwright-cli cookie-list --domain=example.com
playwright-cli cookie-get session_id
playwright-cli cookie-set session_id abc123 --httpOnly --secure
playwright-cli cookie-delete session_id / cookie-clear
playwright-cli localstorage-get theme / localstorage-set theme dark
playwright-cli sessionstorage-list / sessionstorage-get step
```

### 3.7 网络拦截与调试

```powershell
playwright-cli route "**/*.jpg" --status=404                     # 拦截图片请求
playwright-cli route "https://api.example.com/**" --body='{"mock": true}'   # mock 接口
playwright-cli route-list / unroute "**/*.jpg" / unroute          # 查看/清除拦截
playwright-cli console warning                       # 查看控制台消息（可过滤级别）
playwright-cli requests                              # 查看捕获的网络请求
playwright-cli request 5                             # 查看第 5 个请求详情
playwright-cli tracing-start / tracing-stop          # 录制 Playwright trace
playwright-cli video-start video.webm / video-stop   # 录制视频
playwright-cli run-code "async page => await page.context().grantPermissions(['geolocation'])"
playwright-cli run-code --filename=script.js         # 执行任意 Playwright 代码
```

### 3.8 对话框

```powershell
playwright-cli dialog-accept                         # 接受 alert/confirm
playwright-cli dialog-accept "confirmation text"     # accept prompt 并输入文本
playwright-cli dialog-dismiss                        # 取消对话框
```

### 3.9 多会话管理

```powershell
playwright-cli -s=mysession open example.com --persistent   # 命名会话
playwright-cli -s=mysession click e6                        # 指定会话操作
playwright-cli list                                         # 列出活动会话
playwright-cli close-all                                    # 关闭全部会话
playwright-cli kill-all                                     # 强杀全部浏览器进程
playwright-cli -s=msedge detach                             # 脱离外部浏览器（保持其运行）
playwright-cli delete-data                                  # 删除默认会话用户数据
```

### 3.10 全局选项

```powershell
playwright-cli --raw snapshot > before.yml   # 只输出结果值（去掉状态/快照路径），可管道
playwright-cli --json list                   # JSON 结构化输出
```

---

## 4. 元素定位方式（按优先级）

```powershell
# 1. 快照 ref（首选，最短、最省 token、无幻觉风险）
playwright-cli click e15

# 2. CSS 选择器
playwright-cli click "#main > button.submit"

# 3. role 定位器
playwright-cli click "getByRole('button', { name: 'Submit' })"

# 4. testid
playwright-cli click "getByTestId('submit-button')"
```

iframe 内元素：快照中以 `f` 前缀 ref 表示（如 `f0e2`），直接使用即可。

### 4.1 常见表单元素操作手册

| 元素类型 | 操作命令 | 要点 |
|---------|---------|------|
| 文本输入框 / textarea | `fill e5 "文本"` | 直接赋值并替换全部内容 |
| 密码框 | `fill e5 "密码"` | 同文本框 |
| 需触发联想/实时校验的输入框 | `click e5` 后 `type "文本"` | **逐键输入**触发 keydown，autocomplete 才会弹出 |
| 原生下拉 `<select>` | `select e9 "option-value"` | value 用 option 的 value 或可见文本 |
| 复选框 checkbox | `check e12` / `uncheck e12` | 多选框组逐个 check |
| 单选框 radio | `check e12` | 同组自动互斥 |
| 开关 switch | `click` 或 `check` | 通常是样式化 checkbox |
| 原生日期 `<input type="date">` | `fill e8 "2026-08-30"` | **必须 ISO 格式 yyyy-MM-dd** |
| 原生多选 `<select multiple>` | run-code（见下） | CLI 的 select 一次只能选一个 |
| 自定义下拉（Ant Design 等） | click 展开 → find → click | 不能用 `select` 命令 |
| 滑块 slider | `drag e2 e8` 或坐标 mousedown/move/up | 也可聚焦后 `press ArrowRight` 微调 |
| 文件上传 | `upload ./file.pdf` | 也可 `drop e4 --path=...` |
| 富文本 contenteditable | `click` 聚焦 → `type` | 或 `eval` 设 innerHTML |
| 提交 | `fill e5 "文本" --submit` / `press Enter` / click 提交按钮 | |

**fill 与 type 的区别**：`fill` 直接赋值不触发逐键键盘事件；`type` 逐键输入。有实时校验、联想搜索的输入框必须用 `type`，普通输入用 `fill` 更快更稳。

**自定义下拉框（div 模拟，非原生 select）**：

```powershell
playwright-cli click e10          # 点击展开下拉面板
playwright-cli find "目标选项"     # 搜索选项，省 token
playwright-cli click e15          # 点击选项
```

**下拉带搜索过滤**：展开 → `type "关键字"` 触发过滤 → `find` 定位候选项 → `click`。

**日期选择器（自定义日历组件）**：

```powershell
# 方式 A：先试直接填（部分组件支持）
playwright-cli fill e8 "2026-08-30"
playwright-cli press Enter

# 方式 B：点出日历面板再点日期
playwright-cli click e8
playwright-cli find "30"
playwright-cli click e20
```

**不知道 option 的 value 时，用 eval 读出所有选项**：

```powershell
playwright-cli eval "el => [...el.options].map(o => o.value + ' : ' + o.text)" e9
```

**原生多选框一次选多个**（run-code 兜底）：

```powershell
playwright-cli run-code "async page => await page.locator('select#tags').selectOption(['a', 'b'])"
```

---

## 5. 典型工作流

### 5.1 表单登录

```powershell
playwright-cli open https://example.com/login --headed
playwright-cli find "用户名"                          # 用 find 定位而不用全量快照
playwright-cli fill e1 "admin" --submit
playwright-cli fill e2 "password123" --submit
playwright-cli snapshot
playwright-cli close
```

### 5.2 保持登录态（跨命令/跨天复用）

```powershell
# 方式 A：持久化 profile（最简单）
playwright-cli open https://example.com --persistent
# 手动或自动登录一次后，后续 open --persistent 均带登录态

# 方式 B：导出/导入 storage state
playwright-cli state-save auth.json
playwright-cli close
playwright-cli open https://example.com
playwright-cli state-load auth.json
```

### 5.3 抓取数据（token 高效姿势）

```powershell
playwright-cli open https://example.com/list
# 用 --raw + eval 直接导出结构化数据，避免读大快照
playwright-cli --raw eval "JSON.stringify([...document.querySelectorAll('.item')].map(a=>({t:a.textContent,h:a.href})))" > data.json
playwright-cli close
```

### 5.4 调试页面报错

```powershell
playwright-cli open http://localhost:5173
playwright-cli click e4
playwright-cli console error            # 只看错误
playwright-cli requests                 # 查看接口请求
```

### 5.5 UI 走查（让用户标注反馈）

```powershell
playwright-cli open https://example.com
playwright-cli show --annotate   # 打开标注面板，用户画框留言后返回截图+快照+备注
```

---

## 6. Windows / PowerShell 注意事项

本工作区通过 RunCommand 工具执行命令，环境为 **PowerShell**：

```powershell
# URL 含 & 时必须整体加双引号（PowerShell 会把裸 & 当命令分隔符截断）
playwright-cli goto "https://example.com/?a=1&b=2"

# 或使用 --% 停止解析符
playwright-cli --% goto "https://example.com/?a=1&b=2"

# cmd.exe 中用 ^& 转义
playwright-cli goto "https://example.com/?a=1^&b=2"
```

- `open` 命令启动 daemon 后**立即返回**，不会阻塞，无需非阻塞执行。
- 快照/截图/视频路径是相对工作区的，用 Read 工具读取时补全绝对路径。

### 6.1 打开本地 HTML 文件（file: 协议被阻止）

playwright-cli 安全策略**禁止 `file:` 协议**，直接 `open "file:///d:/.../page.html"` 会报错：
`Error: Access to "file:" protocol is blocked`。

**解决方案**：用本地 HTTP 服务器托管文件后再访问（已验证可行）：

```powershell
# 1. 在目标目录起静态服务（非阻塞后台运行，-s 静默日志）
npx -y http-server "d:\path\to\dir" -p 8765 -s

# 2. 浏览器导航到 localhost 地址
playwright-cli goto "http://localhost:8765/page.html"
```

- 选一个不常用端口（如 8765）避免冲突；任务结束后记得停掉服务进程。
- 替代方案：`python -m http.server 8765`（需 Python）或 `npx -y serve -l 8765`。

### 6.2 打开 SSL/TLS 证书异常的网站（自签名/过期/域名不匹配）

访问证书异常的站点时浏览器会拦截（如 `NET::ERR_CERT_AUTHORITY_INVALID`）。playwright-cli 没有 `--insecure` 之类的命令行参数，需通过 **config 文件**设置 `contextOptions.ignoreHTTPSErrors: true`（已验证可行）：

```json
// .playwright/ssl-config.json
{
  "browser": {
    "browserName": "chromium",
    "contextOptions": {
      "ignoreHTTPSErrors": true
    }
  }
}
```

```powershell
# 用指定 config 启动会话（建议用命名会话，避免影响默认会话）
playwright-cli -s=ssltest --config .playwright/ssl-config.json open https://self-signed.badssl.com --headed
# 验证：页面标题能正常返回即生效；用完关闭
playwright-cli -s=ssltest close
```

要点：
- config 在浏览器启动时加载，**已运行的会话不生效**，必须（重新）`open` 时带上 `--config`。
- config 默认查找路径为 `.playwright/cli.config.json`，放这里则无需每次传 `--config`。
- `contextOptions` 支持全部 Playwright `BrowserContextOptions`（viewport、userAgent 等），`launchOptions` 支持 `channel`、`executablePath` 等启动参数。
- `ignoreHTTPSErrors` 仅用于测试/内网环境，不要对不可信公网站点使用。

### 6.3 特殊网页的处理流程速查

**HTTP Basic Auth（401 原生认证框）**：`dialog-accept` 对原生认证框无效，需 config 预置凭据：

```json
"contextOptions": { "httpCredentials": { "username": "admin", "password": "123456" } }
```

**Canvas / WebGL 页面（地图、游戏、图表库）**：无 DOM 元素，snapshot 几乎为空，ref 定位失效，改用坐标级操作：

```powershell
playwright-cli screenshot            # 截图确认位置
playwright-cli mousemove 400 300     # 移动到坐标
playwright-cli mousedown / mouseup   # 点击
playwright-cli mousewheel 0 200      # 缩放/滚动
```

**无限滚动 / 懒加载列表**：内容随滚动才加载，先滚再取：

```powershell
playwright-cli mousewheel 0 2000
playwright-cli run-code "async page => await page.mouse.wheel(0, 2000)"   # 连续滚动
playwright-cli snapshot              # 滚动后再快照获取新内容
```

**WebSocket / SSE 长连接页面**：连接常驻导致 `networkidle` 永不触发，等待会挂起。改用：

```powershell
playwright-cli run-code "async page => await page.goto('https://xx', { waitUntil: 'domcontentloaded' })"
playwright-cli run-code "async page => await page.waitForTimeout(3000)"
```

**验证码 / 人机验证（Cloudflare、滑块）**：不要绕过。`--headed` 打开 → 人工完成验证 → 配合 `--persistent` 让验证结果落盘复用；或 `playwright-cli show` 打开面板人工接管。

**其他场景**：

| 场景 | 方案 |
|------|------|
| `window.open` 弹出新窗口 | `tab-list` 查看 → `tab-select n` 切换 |
| 自定义请求头（反向代理鉴权等） | config `contextOptions.extraHTTPHeaders` |
| 指定语言/时区/地理位置 | config `contextOptions.locale` / `timezoneId` / `geolocation` |
| 企业代理内网 | 环境变量 `PLAYWRIGHT_MCP_PROXY_SERVER=http://proxy:3128` |
| 文件下载 | config `outputDir` 指定输出目录，文件落在其中 |
| mTLS 客户端证书 | config `contextOptions.clientCertificates` |
| SPA 路由切换 | ref 过期，每次路由后重新 `snapshot` |

---

## 7. 常见问题与解决方案

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| `playwright-cli` 不是内部或外部命令 | 未全局安装 | `npm install -g @playwright/cli@latest`；或改用 `npx playwright cli <cmd>` |
| 打开浏览器报错缺少二进制 | 无 Chrome 且未装浏览器 | `playwright-cli install-browser`；推荐直接安装系统 Chrome |
| `click e15` 报 ref 不存在 | 页面已变化，旧快照 ref 过期 | 重新 `playwright-cli snapshot` 用新 ref；SPA 路由切换后必刷快照 |
| 找不到某元素 | 元素在快照深层级或被隐藏 | `playwright-cli find "文本"` 搜索；或 `snapshot --depth=4` 先看结构；用 `eval` 查 DOM |
| 点击无反应 | 元素被遮挡/需要先悬停 | 先 `hover` 再 `click`；或用 `eval "el => el.click()" e5` 强制触发 |
| alert/confirm 弹出后命令卡住 | 对话框阻塞页面 | 立即执行 `dialog-accept` 或 `dialog-dismiss` |
| 登录态每次都丢 | 默认 profile 在内存中 | `open --persistent`；或 `state-save`/`state-load` |
| 浏览器进程越积越多 | 会话未关闭 | `playwright-cli list` 查看；`close-all` 正常关闭；`kill-all` 强杀 |
| 输出内容太大浪费 token | 全量快照/全页截图 | 用 `find` 搜索代替全量读取；`snapshot --depth=4`；快照单元素；`--raw` 只取值 |
| 截图空白/页面未加载完 | SPA 渲染慢 | 用 `run-code "async page => await page.waitForTimeout(3000)"` 等待后再 snapshot |
| 想看界面但无窗口 | 默认无头模式 | `open --headed`；已运行的会话需 `close` 后重新 open |
| URL 参数 `&` 后内容丢失 | PowerShell/cmd 解析 `&` | URL 整体加双引号，或 `--%`（见第 6 节） |
| 多项目/多浏览器互相干扰 | 共用默认会话 | 各用命名会话 `-s=projA`、`-s=projB` |
| socket/daemon 连接异常 | 守护进程僵死 | `playwright-cli kill-all` 后重新 `open` |
| mock 不生效 | route pattern 不匹配或未在请求前设置 | 先 `route` 再触发导航/请求；`route-list` 确认已注册；pattern 用 `**/*.json` 通配 |
| 文件上传无效 | 直接 fill 文件路径不行 | 用 `upload ./file.pdf` 或 `drop e4 --path=...` |
| 打开本地 HTML 报 `Access to "file:" protocol is blocked` | 安全策略禁止 file: 协议 | 起本地 HTTP 服务再访问，见 6.1 节（`npx -y http-server <dir> -p 8765 -s`） |
| 证书异常站点被拦截（自签名/过期/域名不匹配） | 浏览器 TLS 校验失败，CLI 无 --insecure 参数 | config 设 `contextOptions.ignoreHTTPSErrors: true` 后重新 open，见 6.2 节 |
| 401 Basic Auth 原生认证框无法处理 | `dialog-accept` 只对 JS 弹窗有效 | config 设 `contextOptions.httpCredentials` 预置凭据，见 6.3 节 |
| 地图/游戏等 Canvas 页面 snapshot 为空 | 页面无 DOM 元素，ref 机制失效 | 用 screenshot + mousemove/mousedown 坐标级操作，见 6.3 节 |
| 等待 networkidle 永远挂起 | WebSocket/SSE 长连接常驻 | 改用 `waitUntil: 'domcontentloaded'` 或固定 waitForTimeout，见 6.3 节 |

---

## 8. 最佳实践

1. **ref 优先**：能用快照 ref 就不用 CSS/role 选择器——最短且杜绝选择器幻觉。
2. **按需读取**：每条命令返回的快照文件路径，只在需要时用 Read 读取；优先 `find` 定点搜索。
3. **两段式快照**：大页面先 `snapshot --depth=4` 概览，再对目标区域 `snapshot e34` 深入。
4. **数据导出用 `--raw eval`**：比读快照再解析高效得多。
5. **少截图**：截图是给用户看的，验证页面状态用 snapshot/find 即可。
6. **调试三件套**：`console`（报错）、`requests`（接口）、`tracing-start/stop`（完整回溯）。
7. **任务收尾**：确认结束后 `close`（或 `close-all`），避免残留浏览器进程。
8. **本工作区选择建议**：
   - 简单浏览/验证页面 → 可用内置 `browser_*` 系列工具（browser_navigate/browser_click 等）。
   - 需要登录态持久化、网络 mock、视频录制、多会话并行、抓取大量结构化数据、或用户明确要求 playwright-cli → 用本 skill 的 CLI 方案。

---

## 9. 命令执行方式（本工作区）

- 所有命令通过 **RunCommand 工具**执行（PowerShell），普通操作用阻塞式即可（命令本身立即返回）。
- 验证安装成功：`playwright-cli --version`。
- 首次使用建议让用户确认已安装 Chrome，否则先执行 `playwright-cli install-browser`。
