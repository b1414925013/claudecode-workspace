"""pyhutool.text - 文本构建与编码工具模块（零依赖）。

对齐 Hutool 的 ``cn.hutool.core.text`` 包，提供：

- ``StringBuilder``  可变字符串构建器（对齐 ``cn.hutool.core.text.StrBuilder``）
- ``UnicodeUtil``    Unicode 转义编解码（对齐 ``cn.hutool.core.util.UnicodeUtil``）
"""

from pyhutool.text.string_builder import StringBuilder
from pyhutool.text.unicode_util import UnicodeUtil

__all__ = ["StringBuilder", "UnicodeUtil"]
