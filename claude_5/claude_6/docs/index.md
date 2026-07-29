# pyhutool

<p align="center"><strong>Hutool 风格的 Python 工具库</strong></p>

!!! info "定位"
    外部 API 对齐 Java [Hutool](https://hutool.cn)，内部用 Python 3.11+ 现代特性重新实现。

## 特性

- **API 对齐** —— 类名 / 方法名 / 参数语义与 Hutool 一一对应
- **Pythonic 实现** —— 不照搬 Java 代码，符合 PEP 8，带完整类型提示
- **核心零依赖** —— 仅用标准库；HTTP / JSON / 加密以 `extras` 按需引入
- **双套异步** —— I/O 模块同时提供 `sync` 与 `async` API
- **严格类型** —— 通过 `mypy --strict`

## 安装

```bash
pip install pyhutool                       # 核心零依赖
pip install "pyhutool[all]"                # 全部高级模块
```

## 快速上手

```python
from pyhutool.core import StrUtil, ObjectUtil

StrUtil.blank_to_default("", "x")          # -> "x"
StrUtil.to_underline_case("camelCase")     # -> "camel_case"
ObjectUtil.default_if_null(None, "y")      # -> "y"
```

下一步：阅读 [快速开始](guide/quickstart.md) 与 [StrUtil 文档](core/str_util.md)。
