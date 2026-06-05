# Claude Code 浏览器自动化方案对比：Agent Browser、Playwright、DevTools

## 一、为什么需要浏览器自动化？

### 传统方式的痛点

假设你想让 AI 帮你做这些事：

- 打开竞品网站，截图看看他们的新功能
- 自动登录公司内部系统，导出报表
- 测试你刚写的网页，看看表单能不能正常提交
- 抓取某个页面的 API 返回值，排查 Bug

如果没有浏览器自动化，你只能：

1. 自己手动打开浏览器
2. 截图或复制内容
3. 粘贴给 AI 看

这不仅麻烦，而且很多动态内容（如需要登录的页面、JavaScript 渲染的内容）根本没法直接给 AI。

### 浏览器自动化的价值

有了浏览器自动化，AI 可以：

```
你说："帮我打开淘宝，搜索 iPhone 16，看看前 5 个商家的价格"

AI 做：
1. 启动浏览器
2. 打开 taobao.com
3. 在搜索框输入 "iPhone 16"
4. 点击搜索按钮
5. 读取前 5 个商品的价格
6. 整理成表格返回给你
```

整个过程你只需要一句话，AI 全程自动完成。

---

## 二、三大方案速览

在深入对比之前，先看一张总览表：

| 特性 | Agent Browser | Playwright MCP | DevTools MCP |
|------|--------------|----------------|--------------|
| **开发者** | Vercel | Microsoft | Google |
| **Token 消耗** | ⭐⭐⭐⭐⭐ 最低 | ⭐⭐ 较高 | ⭐⭐⭐ 中等 |
| **响应速度** | ⭐⭐⭐⭐⭐ 最快 | ⭐⭐⭐ 中等 | ⭐⭐⭐⭐ 较快 |
| **功能完整性** | ⭐⭐⭐ 基础 | ⭐⭐⭐⭐⭐ 最全 | ⭐⭐⭐⭐ 丰富 |
| **调试能力** | ⭐⭐ 有限 | ⭐⭐⭐ 中等 | ⭐⭐⭐⭐⭐ 最强 |
| **稳定性** | ⭐⭐⭐⭐ 较好 | ⭐⭐⭐⭐⭐ 最佳 | ⭐⭐⭐⭐ 较好 |
| **学习成本** | ⭐⭐⭐⭐⭐ 最低 | ⭐⭐⭐ 中等 | ⭐⭐ 较高 |

**一句话总结：**

- **Agent Browser**: 轻量快速，日常浏览首选
- **Playwright MCP**: 专业稳定，测试流程首选
- **DevTools MCP**: 调试利器，开发排错首选

---

## 三、深入对比：各有什么绝活？

### Agent Browser：快如闪电的"轻骑兵"

Agent Browser 是 Vercel 专门为 AI Agent 设计的浏览器自动化工具。它的核心设计理念是：**用最少的信息，让 AI 理解网页**。

#### 核心机制：Snapshot + Refs

传统方案会把整个网页的 DOM 树或可访问性树发给 AI，动辄几万 Token。Agent Browser 不这样做——它只发送一个精简的"快照"，并给每个可交互元素分配一个简短的引用 ID（ref）。

```
# Agent Browser 的快照格式
- button "登录" [ref=e1]
- input "用户名" [ref=e2]
- input "密码" [ref=e3]
- link "忘记密码" [ref=e4]
```

AI 看到的就是这么简洁的结构。当它想点击"登录"按钮时，只需要说"点击 e1"，而不需要理解复杂的 CSS 选择器或 XPath。

#### Token 消耗对比

| 操作 | Playwright MCP | Agent Browser | 节省比例 |
|------|----------------|---------------|---------|
| 打开页面 | ~15,000 tokens | ~1,000 tokens | **93%** |
| 点击按钮 | ~12,000 tokens | ~800 tokens | **93%** |
| 填写表单 | ~18,000 tokens | ~1,200 tokens | **93%** |

减少 93% 的 Token 消耗，意味着：

- 响应速度更快（AI 处理的信息更少）
- 成本更低（按 Token 计费的话）
- 更少触发上下文长度限制

#### 适用场景

✅ **最适合**:
- 快速浏览网页内容
- 简单的表单填写
- 截图和内容提取
- 日常轻量级自动化

❌ **不适合**:
- 复杂的多步骤测试流程
- 需要精确控制的场景
- 需要深度调试的情况

#### 安装和使用

```bash
# 安装
npm install -g @anthropic-ai/agent-browser

# 在 Claude Code 中使用（作为 Skill）
# 直接用自然语言指挥即可
"用 Agent Browser 打开 https://example.com，截个图"
```

---

### Playwright MCP：稳如泰山的"重装步兵"

Playwright 是 Microsoft 开发的老牌浏览器自动化框架，被全球无数公司用于 E2E 测试。Playwright MCP 是它的 AI 扩展版，专门适配 Claude Code 等 AI 工具。

#### 核心机制：Accessibility Tree（可访问性树）

Playwright 会把网页的完整可访问性树发送给 AI。这棵树包含了页面上所有元素的详细信息：角色、名称、状态、层级关系等。

```
# Playwright 的可访问性树片段
- document
  - navigation
    - link "首页"
    - link "产品"
    - link "关于我们"
  - main
    - heading "欢迎" [level=1]
    - form
      - textbox "用户名" [required]
      - textbox "密码" [required] [type=password]
      - button "登录"
```

信息更全面，但 Token 消耗也更高。

#### 独特优势：跨浏览器 + 专业测试能力

Playwright 支持三大浏览器引擎：

- **Chromium**（Chrome、Edge）
- **Firefox**
- **WebKit**（Safari）

这意味着你可以用同一套指令，测试你的网站在不同浏览器上的表现。

此外，Playwright 还有很多专业测试特性：

- ✅ **自动等待**: 元素可交互后才操作，不怕页面加载慢
- ✅ **网络拦截**: 可以 mock API 返回值
- ✅ **多标签页管理**: 同时操控多个页面
- ✅ **视频录制**: 自动录制操作过程

#### 适用场景

✅ **最适合**:
- E2E 自动化测试
- 复杂的用户流程测试
- 跨浏览器兼容性测试
- 需要高稳定性的生产环境

❌ **不适合**:
- 简单的快速浏览
- Token 预算有限的场景
- 不需要完整测试能力的情况

#### 安装和配置

```json
// claude_desktop_config.json 或 settings.json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@anthropic-ai/mcp-server-playwright"]
    }
  }
}
```

---

### DevTools MCP：洞察秋毫的"侦察兵"

DevTools MCP 是 Google 官方出品，直接封装了 Chrome DevTools Protocol（CDP）。如果你用过 Chrome 的开发者工具（F12），你就知道它有多强大。

#### 核心机制：Chrome DevTools Protocol

CDP 是 Chrome 浏览器的"后门"，通过它可以访问浏览器的几乎所有内部信息：

- Console 输出
- Network 请求和响应
- DOM 结构和样式
- JavaScript 执行环境
- 性能指标
- …

DevTools MCP 把这些能力暴露给 AI，让 AI 成为你的"高级调试助手"。

#### 独特优势：调试能力无敌

其他两个方案侧重于"操作"浏览器，DevTools MCP 侧重于"理解"浏览器内部发生了什么。

```
你说："页面白屏了，帮我查查原因"

DevTools MCP 会：
1. 检查 Console 有没有报错
2. 查看 Network 请求是否失败
3. 分析 JavaScript 执行是否有异常
4. 检查关键元素是否正常渲染
5. 给出诊断结论
```

这是其他方案做不到的。

#### 适用场景

✅ **最适合**:
- 前端开发调试
- 性能分析和优化
- 网络请求排查
- JavaScript 错误诊断

❌ **不适合**:
- 简单的页面浏览
- 不需要深度调试的场景
- 非 Chrome 浏览器

#### 安装和配置

DevTools MCP 需要配合 Chrome 扩展使用：

**1. 安装 MCP Server：**

```json
{
  "mcpServers": {
    "devtools": {
      "command": "npx",
      "args": ["@anthropic-ai/mcp-server-chrome-devtools"]
    }
  }
}
```

**2. 在 Chrome 中安装配套扩展**（从 Chrome Web Store）

**3. 启动 Chrome 时开启远程调试：**

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# Windows
chrome.exe --remote-debugging-port=9222
```

---

## 四、实战选择指南

### 场景一：我就想让 AI 帮我看看网页

**推荐：Agent Browser**

你只是想让 AI 打开某个网页、截个图、看看内容，不需要复杂操作。Agent Browser 最快、最省 Token。

```
"帮我打开 competitor.com，看看他们的定价页面"
"截个图给我看看首页长什么样"
"这个表单能不能正常显示"
```

### 场景二：我需要测试复杂的用户流程

**推荐：Playwright MCP**

注册、登录、下单、支付、退出——这种多步骤流程需要稳定可靠的执行。Playwright 的自动等待和错误恢复机制让它非常适合这类任务。

```
"测试一下用户注册流程：填写表单→验证邮箱→完善资料→跳转到主页"
"每天早上 9 点自动运行这个测试脚本"
```

### 场景三：我的页面有 Bug，需要排查

**推荐：DevTools MCP**

页面白屏、接口报错、样式错乱——这些问题需要深入浏览器内部才能定位。DevTools MCP 是唯一能直接访问 Console、Network、DOM 的方案。

```
"页面打开后一直在转圈，帮我看看是哪个接口卡住了"
"这个按钮点击后没反应，帮我查查有没有 JS 报错"
```

### 场景四：我需要同时具备多种能力

**可以组合使用！**

三个方案并不互斥，你完全可以同时配置，让 AI 根据任务自动选择最合适的工具。

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@anthropic-ai/mcp-server-playwright"]
    },
    "devtools": {
      "command": "npx",
      "args": ["@anthropic-ai/mcp-server-chrome-devtools"]
    }
  }
}
```

再加上 Agent Browser 的 Skill，你就拥有了完整的浏览器自动化能力矩阵。

---

## 五、进阶技巧

### 1. 保存登录状态

很多网站需要登录才能访问，每次都手动登录很麻烦。你可以让 AI 保存 Cookie：

```
"用 Agent Browser 打开 xxx.com，让我登录，然后保存登录信息"
```

下次访问时，AI 会自动加载之前保存的 Cookie，无需重新登录。

### 2. 无头模式

如果你不需要看到浏览器界面（比如在服务器上运行），可以使用无头模式：

```
"用 Playwright 在无头模式下测试登录流程"
```

### 3. 截图对比

开发前端时，经常需要对比修改前后的效果。可以这样做：

```
"截图保存为 before.png"
# 修改代码
"再截一张图保存为 after.png，然后对比两张图的差异"
```

### 4. 批量操作

需要对多个页面执行相同操作时：

```
"依次打开这 10 个 URL，截图保存到 screenshots 文件夹"
```

---

## 六、常见问题

### Q1：为什么我的 Playwright MCP 连接不上？

检查几个常见问题：

1. 确保已安装 Node.js 18+
2. 确保 MCP Server 配置正确
3. 尝试手动运行 `npx @anthropic-ai/mcp-server-playwright` 看报错

### Q2：DevTools MCP 提示"无法连接到 Chrome"？

确保：

1. Chrome 已启动并开启了远程调试端口（9222）
2. 没有其他程序占用该端口
3. Chrome 扩展已安装并启用

### Q3：Agent Browser 截图是空白的？

可能是页面还没加载完。尝试：

```
"打开页面后等待 3 秒再截图"
```

### Q4：哪个方案最稳定？

如果追求稳定性，**Playwright MCP** 是最佳选择。它有完善的等待机制和错误处理，是生产级的自动化框架。

### Q5：Token 真的差这么多吗？

是的。在实际测试中，执行相同的 10 步操作：

- **Playwright MCP**: 约 100,000 tokens
- **DevTools MCP**: 约 50,000 tokens
- **Agent Browser**: 约 7,000 tokens

差距确实很大，尤其是在需要频繁操作浏览器的场景下。

---

## 总结

记住这个口诀：

- **看看、填表** → Agent Browser
- **测试、跑流程** → Playwright MCP
- **调试、抓请求** → DevTools MCP

