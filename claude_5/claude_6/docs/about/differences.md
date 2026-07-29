# 与 Hutool 的差异

## 命名约定

| 方面 | Hutool | pyhutool | 原因 |
|------|--------|----------|------|
| 方法名 | `camelCase` | `snake_case` | PEP 8 |
| 类名 | `StrUtil` | `StrUtil`（保留） | 便于迁移 |
| 异常后缀 | `*Exception` | `*Error` | PEP 8 |
| 空值 | `null` | `None` | 语言差异 |

## 容器类型

Hutool 大量使用 `CollUtil.newArrayList()` 等，pyhutool 直接使用 Python 内置容器：

```python
# Hutool
List<String> list = CollUtil.newArrayList("a", "b");

# pyhutool
lst = ["a", "b"]   # 直接用 list
```

`CollUtil` 仅提供容器之上的工具方法（如 `join`、`zip`、`group_by`）。

## 异步

Hutool 不支持异步。pyhutool 在 HTTP / IO 模块提供 `a` 前缀的异步版本：

| 同步 | 异步 |
|------|------|
| `HttpUtil.get()` | `HttpUtil.aget()` |
| `FileUtil.read_file()` | `FileUtil.aread_file()` |

## 依赖哲学

| | Hutool | pyhutool |
|--|--------|----------|
| 核心 | 零依赖 | 零依赖 |
| HTTP | 自研 | httpx |
| JSON | 自研 | orjson |
| 加密 | JDK + Bouncy | cryptography |

pyhutool 倾向复用成熟的 Python 生态库，避免重复造轮子。
