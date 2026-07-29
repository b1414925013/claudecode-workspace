# pyhutool

<p align="center">
  <strong>Hutool 风格的 Python 工具库</strong>
</p>

> 外部 API 对齐 Java [Hutool](https://hutool.cn)，内部用 Python 3.11+ 现代特性重新实现。

## 设计理念

- **API 对齐**：类名 / 方法名 / 参数语义与 Hutool 一一对应，Java 背景开发者零成本上手。
- **Pythonic 实现**：内部不照搬 Java 代码，充分利用标准库与类型提示，符合 PEP 8。
- **核心零依赖**：仅依赖 Python 标准库；HTTP / JSON / 加密等高级能力以 `extras` 形式按需引入。
- **完整类型**：所有公共 API 配类型提示，通过 `mypy --strict`。
- **双套异步**：I/O 模块同时提供 `sync` 与 `async` 两套 API。

## 安装

```bash
# 核心（零依赖）
pip install pyhutool

# 按需引入高级模块
pip install "pyhutool[http]"          # httpx
pip install "pyhutool[json]"          # orjson
pip install "pyhutool[crypto]"        # cryptography
pip install "pyhutool[jwt]"           # pyjwt + cryptography
pip install "pyhutool[cron]"          # APScheduler
pip install "pyhutool[ssh]"           # paramiko
pip install "pyhutool[all]"           # 全部
```

## 快速示例

```python
from pyhutool.core import StrUtil, ObjectUtil

# 字符串工具
StrUtil.blank_to_default("", "default")     # -> "default"
StrUtil.format("hello {}", "world")         # -> "hello world"
StrUtil.to_underline_case("camelCase")      # -> "camel_case"

# 对象工具
ObjectUtil.default_if_null(None, "x")       # -> "x"
ObjectUtil.is_empty([])                      # -> True
ObjectUtil.clone({"a": [1, 2, 3]})           # 深拷贝
```

## 模块路线图

| 模块 | 状态 | 依赖 |
|------|------|------|
| `pyhutool.core` (StrUtil/ObjectUtil/DateUtil/CollUtil/NumUtil/RandomUtil/IdUtil/RegexUtil) | ✅ 已完成 | 标准库 |
| `pyhutool.text` (StringBuilder/UnicodeUtil) | ✅ 已完成 | 标准库 |
| `pyhutool.io` (IoUtil/FileUtil/ResourceUtil, sync+async) | ✅ 已完成 | 标准库 |
| `pyhutool.json` (JsonUtil) | ✅ 已完成 | orjson |
| `pyhutool.http` (HttpUtil/AsyncHttpUtil/HttpResponse) | ✅ 已完成 | httpx |
| `pyhutool.crypto` (CryptoUtil/DigestUtil) | ✅ 已完成 | cryptography (CryptoUtil)；标准库 (DigestUtil) |
| `pyhutool.jwt` (JWTUtil/JWT) | ✅ 已完成 | pyjwt |
| `pyhutool.cron` (CronUtil) | ✅ 已完成 | APScheduler |
| `pyhutool.extra.ssh` (JschUtil) | ✅ 已完成 | paramiko |

## 与 Hutool 的差异

| 方面 | Hutool (Java) | pyhutool (Python) |
|------|---------------|-------------------|
| 命名 | `camelCase` 方法 | `snake_case` 方法，保留类名 |
| 空值 | `null` | `None` |
| 异常 | `*Exception` 后缀 | `*Error` 后缀 (PEP 8) |
| 异步 | 不支持 | I/O 模块双套 sync+async |
| 集合 | `CollectionUtil` | 直接用 Python 内置容器 |

## 开发

```bash
# 安装开发依赖
pip install -e ".[all]"
pip install ruff black isort mypy pytest pytest-asyncio pytest-cov pre-commit

# 本地检查
ruff check src tests
black --check src tests
isort --check-only src tests
mypy
pytest --cov=pyhutool --cov-fail-under=85

# 安装 pre-commit 钩子
pre-commit install
```

## 许可证

[Apache License 2.0](LICENSE)，与 Hutool 保持一致。
