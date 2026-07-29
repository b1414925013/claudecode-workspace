# 设计理念

## 三大原则

### 1. API 对齐 Hutool

类名、方法名、参数顺序、返回语义与 Java Hutool 一一对应。例如：

| Hutool | pyhutool |
|--------|----------|
| `StrUtil.format("{}", x)` | `StrUtil.format("{}", x)` |
| `StrUtil.isBlank(s)` | `StrUtil.is_blank(s)` |
| `ObjectUtil.defaultIfNull(o, d)` | `ObjectUtil.default_if_null(o, d)` |

Java 背景开发者无需查文档即可上手。

### 2. 内部 Pythonic 重实现

不照搬 Java 代码逻辑，而是用 Python 3.11+ 的现代特性重新实现：

- 类型提示 + `mypy --strict`
- `match-case`、`Self` 类型、PEP 604 联合类型
- 直接使用 Python 内置容器，而非 Java `ArrayList/HashMap`

### 3. 分层可选依赖

```
核心（零依赖）          HTTP / JSON / Crypto / JWT（extras）
┌─────────────┐         ┌──────────────────────┐
│ pyhutool.core│ ←可选→ │ pyhutool.http (httpx) │
│ pyhutool.io  │         │ pyhutool.json (orjson) │
└─────────────┘         └──────────────────────┘
```

## 异步策略

I/O 密集型模块（HTTP、文件）同时提供两套 API：

```python
resp = HttpUtil.get(url)          # 同步
resp = await HttpUtil.aget(url)    # 异步（前缀 a）
```

底层通过 `_compat` 适配层共享请求构建逻辑，避免代码重复。
