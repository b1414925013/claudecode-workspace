# 快速开始

## 安装

```bash
pip install pyhutool
```

需要 HTTP / JSON / 加密等高级模块时：

```bash
pip install "pyhutool[http]"
pip install "pyhutool[crypto,jwt]"
pip install "pyhutool[all]"
```

## 第一个示例

```python
from pyhutool.core import StrUtil

# 空值处理
StrUtil.blank_to_default(user_input, "anonymous")

# 占位符格式化
StrUtil.format("用户 {} 的年龄是 {}", "Tom", 18)

# 命名转换
StrUtil.to_underline_case("userId")   # -> "user_id"
StrUtil.to_camel_case("user_id")      # -> "userId"
```

## 设计约定

| 方面 | pyhutool |
|------|----------|
| 方法命名 | `snake_case`（保留 Hutool 类名） |
| 空值表示 | `None`（Hutool 用 `null`） |
| 异常后缀 | `*Error`（PEP 8），对应 Hutool `*Exception` |
| 容器 | 直接使用 Python 内置 `list/dict/set` |

详见 [与 Hutool 的差异](../about/differences.md)。
