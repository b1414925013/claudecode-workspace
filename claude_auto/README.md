# Claude Code 自动化测试工具

自动解析需求文档，生成标准化测试用例，通过 Claude API 执行接口测试，或通过 Playwright MCP 驱动真实浏览器执行 UI 测试，输出可视化测试报告。

---

## 目录结构

```
claude_auto/
├── main.py                          # 主入口
├── config.yaml                      # 配置文件
├── requirements.txt                 # Python 依赖
├── README.md
├── core/
│   ├── config.py                    # 配置管理（单例）
│   ├── doc_parser.py                # 文档解析 (.md / .docx / .pdf)
│   ├── claude_client.py             # Claude API 客户端
│   ├── testcase_generator.py        # 测试用例生成与执行
│   ├── playwright_executor.py       # Playwright MCP 计划生成
│   └── reporter.py                  # 报告生成 (JSON/MD/HTML)
├── test_docs/                       # 放置需求文档
│   ├── sample.md
│   └── ...
├── output/
│   ├── run_20260503_143000/         # 每次运行一个独立目录
│   │   ├── run.log                  # 运行日志
│   │   ├── test_cases/              # 测试用例 + MCP 计划 + 结果
│   │   ├── reports/                 # 测试报告
│   │   └── screenshots/             # 浏览器截图
│   ├── run_20260503_150000/
│   │   └── ...
│   └── ...
└── logs/                            # 历史日志汇总
```

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

编辑 `config.yaml`：

```yaml
claude:
  api_key: "sk-xxx"                  # API 密钥（必填）
  base_url: ""                        # 留空=Anthropic 官方
  # base_url: "https://api.deepseek.com/anthropic"   # 第三方兼容接口
  model: "claude-sonnet-4-20250514"  # 或 "deepseek-chat"

playwright:
  base_url: "http://localhost:3000"   # 被测应用地址（UI 测试用）
```

### 3. 放入文档

将需求文档（`.md` / `.docx` / `.pdf`）放入 `test_docs/` 目录。

### 4. CLI 参数

| 参数 | 说明 |
|---|---|
|（无参数） | 完整流程：解析 → 生成 → 执行 → 报告 |
| `--execute` | 仅执行已生成的用例（配合 `execution.mode: manual`） |
| `--playwright` | 生成 MCP 测试计划 + 执行说明书，通过 Playwright MCP 执行 |
| `--playwright --report-only` | 加载执行结果，仅生成报告 |
| `--playwright --report-only --run run_xxx` | 指定历史 run 出报告，默认用最新 |
| `--help` | 查看所有参数 |

每次运行输出保存在独立目录 `output/run_{时间戳}/` 下，多次运行互不干扰。

---

## 三种运行模式

### 模式一：AI 自动模式（默认）

```bash
python main.py
```

流程：`解析文档 → AI 生成用例 → AI 执行用例 → 输出报告`

文档内容通过 Claude API 生成测试用例，再由 AI 模拟执行并判定结果。适合**接口测试、逻辑验证、不需要真实浏览器**的场景。

### 模式二：AI 分步模式

在 `config.yaml` 中设置：

```yaml
execution:
  mode: "manual"      # auto=自动执行, manual=分步执行
```

```bash
# 步骤 1：仅生成测试用例（保存为 JSON + DOCX + XLSX）
python main.py

# 步骤 2：执行已生成的用例并生成报告
python main.py --execute
```

适合先评审测试用例、确认无误后再执行的场景。

### 模式三：Playwright MCP UI 测试

通过 Playwright MCP 驱动真实浏览器，逐条执行测试操作并截图。

```bash
# 步骤 1：生成 MCP 测试计划
python main.py --playwright
```

生成 `playwright_plan.json`（结构化操作计划）和 `mcp_instructions.md`（MCP 执行说明书），每条步骤映射到 Playwright MCP 工具：

```
browser_navigate({url})          → 打开页面
browser_fill({selector, value})  → 输入内容
browser_click({selector})        → 点击元素
browser_snapshot()               → 验证页面状态
browser_screenshot({path})       → 保存截图
```

```bash
# 步骤 2：通过 Playwright MCP 执行测试
# 读取 mcp_instructions.md，按说明书调用 MCP 工具
# 执行完毕后将结果填入 playwright_results.json

# 步骤 3：生成测试报告
python main.py --playwright --report-only --run run_20260503_143000
```

输出包含通过/失败统计和截图的 HTML 报告。

---

## 配置文件说明 (`config.yaml`)

| 配置项 | 说明 | 默认值 |
|---|---|---|
| `claude.api_key` | API 密钥（必填） | — |
| `claude.base_url` | API 地址，留空用 Anthropic 官方 | `""` |
| `claude.model` | 模型名称 | `claude-sonnet-4-20250514` |
| `claude.max_tokens` | 最大 Token 数 | `4096` |
| `claude.temperature` | 生成温度 | `0.3` |
| `playwright.base_url` | 被测应用地址 | `http://localhost:3000` |
| `playwright.headless` | 无头模式 | `true` |
| `paths.docs` | 文档目录 | `test_docs` |
| `paths.testcase_output` | 用例输出目录 | `output/test_cases` |
| `paths.report_output` | 报告输出目录 | `output/reports` |
| `paths.logs` | 日志目录 | `logs` |
| `logging.enabled` | 启用文件日志 | `true` |
| `logging.level` | 日志级别 | `INFO` |
| `execution.mode` | 执行策略：`auto` 生成后立即执行，`manual` 仅生成 | `auto` |

---

## 输出说明

每次运行的所有输出位于独立目录 `output/run_{时间戳}/` 下。

```
output/run_20260503_143000/
├── run.log                              # 运行日志
├── test_cases/
│   ├── test_cases_{时间戳}.json         # AI 生成的原始用例
│   ├── test_cases_{时间戳}.docx         # Word 文档
│   ├── test_cases_{时间戳}.xlsx         # Excel 工作簿
│   ├── playwright_plan.json             # MCP 浏览器操作计划
│   ├── mcp_instructions.md              # MCP 执行说明书
│   └── playwright_results.json          # 执行结果
├── reports/
│   ├── report_{时间戳}.json             # JSON 报告
│   ├── report_{时间戳}.md               # Markdown 报告
│   └── report_{时间戳}.html             # HTML 可视化报告（含截图）
└── screenshots/
    ├── TC-Search-001_step_00.png        # 每步操作截图
    └── ...
```

### HTML 报告特点

- **统计仪表盘**：总数 / 通过 / 失败 / 错误 / 通过率
- **通过率进度条**：绿色渐变条
- **用例列表**：点击跳转到详情
- **截图展示**：每步操作截图自动嵌入
- **返回顶部按钮**：响应式布局

---

## 模块说明

| 模块 | 职责 |
|---|---|
| `main.py` | 入口，编排完整流程 |
| `core/config.py` | 读取 `config.yaml`，提供类型化配置 |
| `core/doc_parser.py` | 解析 `.md` / `.docx` / `.pdf` 文档 |
| `core/claude_client.py` | Anthropic SDK 封装，含自动重试 |
| `core/testcase_generator.py` | AI 生成测试用例 + API 执行 |
| `core/playwright_executor.py` | 测试步骤 → MCP 浏览器操作计划 + MCP 执行手册 |
| `core/reporter.py` | 输出 JSON / Markdown / HTML 报告 |

---

## 支持文档格式

- Markdown (`.md`)
- Word (`.doc` / `.docx`)
- PDF (`.pdf`)
