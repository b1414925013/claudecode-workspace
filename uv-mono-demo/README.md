# uv-mono-demo

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-0.8%2B-ffd700)](https://docs.astral.sh/uv/)

一个使用 [uv](https://docs.astral.sh/uv/) 构建的 Python monorepo 项目，演示 UV workspace 多子项目管理与跨包调用。

---

## 目录结构

```
uv-mono-demo/
├── pyproject.toml              # 根工作区配置 — [tool.uv.workspace] 声明所有子项目
├── uv.lock                     # 统一锁定文件，保证全项目依赖一致
├── .gitignore
├── packages/                   # 库项目 —— 被其他项目依赖
│   ├── core/                   # 底层公共工具包
│   ├── service-a/              # 业务项目 A，依赖 core
│   └── service-b/              # 业务项目 B，依赖 core + service-a
└── apps/                       # 应用项目 —— 可执行入口
    └── cli-tool/               # CLI 入口应用，依赖 service-b
```

## 项目依赖关系

```
cli-tool  ──→  service-b  ──→  service-a
                    │                │
                    └──────┬─────────┘
                           ▼
                        core (requests)
```

| 项目 | 类型 | 依赖 | 说明 |
|------|------|------|------|
| `core` | 库 | `requests` | 公共工具函数：`add()`, `greet()`, `celsius_to_fahrenheit()`, `Provider` 类 |
| `service-a` | 库 | `core` | 业务逻辑：`double_greet()`, `temperature_report()` |
| `service-b` | 库 | `core`, `service-a` | 编排层：`run()`, `summarize()` |
| `cli-tool` | 应用 | `service-b` | 命令行入口：`python -m cli_tool` |

## 快速开始

### 前置条件

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/getting-started/installation/) >= 0.5

### 安装

```bash
# 克隆项目后，在根目录安装全部子项目依赖
uv sync
```

### 运行

```bash
# CLI 入口（推荐）
uv run --package cli-tool python -m cli_tool

# 直接运行某个子项目
uv run --package service-b python -c "from service_b import run; run()"
uv run --package service-a python -c "from service_a import temperature_report; print(temperature_report(25))"

# 运行 Python 模块
uv run --package core python -c "from core import add, greet; print(add(1,2)); print(greet('uv'))"
```

### 预期输出

```
========================================
  CLI Tool — 演示完整调用链路
========================================
=== core 直接调用 ===
add(10, 20) = 30
Hello, service_b!

=== service_a 调用 ===
[service-a] greeting World once
[service-a] greeting World again
100.0°C = 212.0°F

=== summarize 聚合演示 ===
items=[3, 7, 10, 15] => {'count': 4, 'total': 35, 'average': 8.75}
```

## UV Workspace 要点

### 根 `pyproject.toml`

```toml
[project]
name = "uv-mono-demo"
version = "0.1.0"
requires-python = ">=3.10"

[tool.uv.workspace]
members = [
  "packages/*",
  "apps/*",
]
```

### 子项目依赖声明

子项目之间通过 `workspace = true` 引用：

```toml
# packages/service-b/pyproject.toml
[project]
dependencies = ["core", "service-a"]

[tool.uv.sources]
core = { workspace = true }
service-a = { workspace = true }

[build-system]
requires = ["uv_build>=0.11.0,<0.12"]
build-backend = "uv_build"
```

关键点：
1. **根目录** 用 `[tool.uv.workspace]` 声明成员 glob
2. **子项目** 用 `dependencies` 列出名称，用 `[tool.uv.sources]` 映射到 workspace
3. **每个子项目** 需要声明 `[build-system]`，否则 uv 无法构建可编辑安装
4. **`uv sync`** 在根目录执行一次，自动安装所有子项目
5. **`uv lock`** 生成单一 `uv.lock`，保证全项目版本一致

## 常用命令

| 命令 | 说明 |
|------|------|
| `uv sync` | 安装/同步所有子项目依赖 |
| `uv lock` | 重新生成锁定文件 |
| `uv tree` | 查看依赖树 |
| `uv run --package <name> <cmd>` | 在指定子项目上下文中运行命令 |
| `uv add --package <name> <pkg>` | 为指定子项目添加依赖 |
| `uv remove --package <name> <pkg>` | 移除指定子项目的依赖 |
| `uv build --package <name>` | 构建指定子项目的分发包 |
| `uv python pin <version>` | 固定项目 Python 版本 |

## 扩展指南

```bash
# 在 packages/ 下新增子项目
mkdir -p packages/my-pkg/src/my_pkg
touch packages/my-pkg/pyproject.toml

# 根目录的 workspace 自动匹配 packages/*，无需修改根配置
uv sync  # 重新安装即可生效
```

## 许可

MIT
