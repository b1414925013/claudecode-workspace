"""Unicode 转义工具。

对齐 Hutool 的 ``cn.hutool.core.util.UnicodeUtil``，提供在 ``\\uXXXX``
转义形式与原始字符串之间的双向转换。

约定
----
- 非 ASCII 字符（码点大于 ``U+007F``）转为 ``\\uXXXX``；
- ASCII 可打印字符保留原样；
- 代理对（emoji、扩展汉字等）按 Hutool 行为输出连续两个 ``\\uXXXX``。
"""

from __future__ import annotations

import re
from typing import Final

__all__ = ["UnicodeUtil"]

# 匹配 \uXXXX 转义序列
_UNICODE_ESCAPE_RE: Final[re.Pattern[str]] = re.compile(r"\\u([0-9a-fA-F]{4})")
# 匹配代理对：高位 D800-DBFF + 低位 DC00-DFFF
_SURROGATE_PAIR_RE: Final[re.Pattern[str]] = re.compile(
    r"\\u([Dd][89A-Ba-b][0-9A-Fa-f]{2})\\u([Dd][C-Fc-f][0-9A-Fa-f]{2})"
)
# ASCII 可打印字符范围
_ASCII_PRINTABLE_MAX: Final[int] = 0x7F


class UnicodeUtil:
    """Unicode 转义编解码工具。"""

    @staticmethod
    def to_unicode(text: str | None) -> str:
        """把字符串转义为 ``\\uXXXX`` 形式。

        对应 Hutool ``UnicodeUtil.toUnicode``。

        Parameters
        ----------
        text:
            原字符串。``None`` 返回空串。
        """
        if not text:
            return ""
        out: list[str] = []
        for ch in text:
            cp = ord(ch)
            if cp <= _ASCII_PRINTABLE_MAX:
                out.append(ch)
            elif cp > 0xFFFF:
                # BMP 之外字符（如 emoji）使用代理对
                cp -= 0x10000
                high = 0xD800 + (cp >> 10)
                low = 0xDC00 + (cp & 0x3FF)
                out.append(f"\\u{high:04x}")
                out.append(f"\\u{low:04x}")
            else:
                out.append(f"\\u{cp:04x}")
        return "".join(out)

    @staticmethod
    def to_string(unicode_str: str | None) -> str:
        """把 ``\\uXXXX`` 形式解码回原字符串。

        对应 Hutool ``UnicodeUtil.toString``。``None`` 返回空串。
        未匹配的字符保持原样。代理对（emoji、扩展汉字等）会被合并为
        单个 BMP 之外字符。
        """
        if not unicode_str:
            return ""

        # 先合并代理对（高位 D800-DBFF + 低位 DC00-DFFF）
        def _replace_pair(m: re.Match[str]) -> str:
            high = int(m.group(1), 16)
            low = int(m.group(2), 16)
            cp = 0x10000 + ((high - 0xD800) << 10) + (low - 0xDC00)
            return chr(cp)

        result = _SURROGATE_PAIR_RE.sub(_replace_pair, unicode_str)

        # 再处理单个 \\uXXXX
        def _replace(m: re.Match[str]) -> str:
            return chr(int(m.group(1), 16))

        return _UNICODE_ESCAPE_RE.sub(_replace, result)

    @staticmethod
    def escape(text: str | None) -> str:
        """``to_unicode`` 的别名，与 ``codecs`` 习惯一致。"""
        return UnicodeUtil.to_unicode(text)

    @staticmethod
    def unescape(text: str | None) -> str:
        """``to_string`` 的别名。"""
        return UnicodeUtil.to_string(text)
