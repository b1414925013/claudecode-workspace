# 异常体系

`pyhutool.core.exceptions` 提供统一的异常层级。

## 层级

| pyhutool | 对应 Hutool | 说明 |
|----------|-------------|------|
| `PyHutoolError` | `HutoolException` | 所有 pyhutool 异常基类 |
| `UtilError` | `UtilException` | 工具运行时异常 |
| `StateError` | `StateException` | 非法状态 |

!!! note "命名差异"
    Python PEP 8 建议异常使用 `Error` 后缀，故 pyhutool 用 `*Error` 而非 Hutool 的 `*Exception`。

## 用法

```python
from pyhutool.core import UtilError, PyHutoolError

try:
    ...
except UtilError as e:
    print(e.message, e.cause)
except PyHutoolError as e:
    # 兜底捕获所有 pyhutool 异常
    ...
```

`PyHutoolError` 携带 `message` 与可选的 `cause` 字段，对应 Java 异常的 cause 链。
