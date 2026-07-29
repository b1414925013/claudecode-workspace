"""字符串工具。

对齐 Hutool 的 ``cn.hutool.core.util.StrUtil``，提供空值判断、占位符格式化、
大小写转换、前后缀处理、填充、分割连接等高频字符串操作。

与 Hutool 的差异：
- 方法名统一为 ``snake_case``；
- 接受 ``str | None`` 输入并在空值时返回安全默认值（与 Hutool ``null`` 处理一致）；
- 异常统一抛出 ``UtilError``。
"""

from __future__ import annotations

import re
import uuid as _uuid
from collections.abc import Iterable

__all__ = ["StrUtil"]

# 匹配 ``{}`` 占位符
_PLACEHOLDER_RE = re.compile(r"\{\}")
# 匹配驼峰边界（用于 to_underline_case）
_CAMEL_BOUNDARY_RE = re.compile(r"([A-Z])")
# 匹配下划线边界（用于 to_camel_case）
_UNDERLINE_BOUNDARY_RE = re.compile(r"_([a-zA-Z])")


class StrUtil:
    """字符串工具类。

    所有方法均为静态方法，对应 Hutool ``StrUtil`` 的静态调用风格，
    例如 ``StrUtil.blank_to_default("", "x")``。
    """

    # ------------------------------------------------------------------
    # 空值判断（对齐 StrUtil.isBlank / isBlank / isEmpty 等）
    # ------------------------------------------------------------------
    @staticmethod
    def is_blank(s: str | None) -> bool:
        """判断字符串是否为空白：``None`` 或仅包含空白字符时返回 ``True``。

        对应 Hutool ``StrUtil.isBlank``。
        """
        if s is None:
            return True
        return s.strip() == ""

    @staticmethod
    def is_not_blank(s: str | None) -> bool:
        """判断字符串是否非空白，等价于 ``not is_blank``。"""
        return not StrUtil.is_blank(s)

    @staticmethod
    def is_empty(s: str | None) -> bool:
        """判断字符串是否为空：``None`` 或长度为 0 时返回 ``True``。

        与 ``is_blank`` 的区别：``is_empty(" ")`` 返回 ``False``。
        """
        return s is None or len(s) == 0

    @staticmethod
    def is_not_empty(s: str | None) -> bool:
        """判断字符串是否非空，等价于 ``not is_empty``。"""
        return not StrUtil.is_empty(s)

    # ------------------------------------------------------------------
    # 空值替换（对齐 blankToDefault / emptyToDefault / nullToDefault）
    # ------------------------------------------------------------------
    @staticmethod
    def blank_to_default(s: str | None, default: str) -> str:
        """若 ``s`` 为空白则返回 ``default``，否则返回 ``s``。"""
        return default if StrUtil.is_blank(s) else s  # type: ignore[return-value]

    @staticmethod
    def empty_to_default(s: str | None, default: str) -> str:
        """若 ``s`` 为空（``None`` 或 ``""``）则返回 ``default``。"""
        return default if StrUtil.is_empty(s) else s  # type: ignore[return-value]

    @staticmethod
    def null_to_default(s: str | None, default: str) -> str:
        """若 ``s`` 为 ``None`` 则返回 ``default``。"""
        return default if s is None else s

    # ------------------------------------------------------------------
    # 格式化（对齐 format / formatWith）
    # ------------------------------------------------------------------
    @staticmethod
    def format(pattern: str | None, *args: object) -> str:
        """使用 ``{}`` 占位符按顺序替换参数。

        对应 Hutool ``StrUtil.format``。

        Examples
        --------
        >>> StrUtil.format("hello {}", "world")
        'hello world'
        >>> StrUtil.format("{}-{}", 1, 2)
        '1-2'
        """
        if pattern is None:
            return ""
        if not args:
            return pattern
        it = iter(args)
        out: list[str] = []
        last_end = 0
        for m in _PLACEHOLDER_RE.finditer(pattern):
            try:
                value = next(it)
            except StopIteration:
                break
            out.append(pattern[last_end : m.start()])
            out.append("" if value is None else str(value))
            last_end = m.end()
        out.append(pattern[last_end:])
        # 消除未匹配的剩余占位符
        return "".join(out)

    @staticmethod
    def format_with(pattern: str | None, placeholder: str, *args: object) -> str:
        """使用自定义占位符按顺序替换参数。

        对应 Hutool ``StrUtil.formatWith``。
        """
        if pattern is None:
            return ""
        if not placeholder:
            raise ValueError("placeholder 不能为空")
        # 用零宽断言保证占位符本身不会被消费
        result = pattern
        for value in args:
            replaced = "" if value is None else str(value)
            result = result.replace(placeholder, replaced, 1)
        return result

    # ------------------------------------------------------------------
    # 截取与前后缀
    # ------------------------------------------------------------------
    @staticmethod
    def sub_pre(s: str | None, length: int) -> str:
        """截取字符串前 ``length`` 个字符。``length`` 为负数时截取到倒数第 ``length`` 个。"""
        if s is None:
            return ""
        if length < 0:
            return s[:length] if -length <= len(s) else s
        return s[:length]

    @staticmethod
    def sub_suf(s: str | None, length: int) -> str:
        """截取字符串后 ``length`` 个字符。"""
        if s is None or length <= 0:
            return ""
        return s[-length:] if length <= len(s) else s

    @staticmethod
    def remove_prefix(s: str | None, prefix: str) -> str:
        """移除前缀（若存在），否则原样返回。"""
        if s is None:
            return ""
        if prefix and s.startswith(prefix):
            return s[len(prefix) :]
        return s

    @staticmethod
    def remove_prefix_ignore_case(s: str | None, prefix: str) -> str:
        """忽略大小写移除前缀。"""
        if s is None:
            return ""
        if prefix and s[: len(prefix)].lower() == prefix.lower():
            return s[len(prefix) :]
        return s

    @staticmethod
    def remove_suffix(s: str | None, suffix: str) -> str:
        """移除后缀（若存在），否则原样返回。"""
        if s is None:
            return ""
        if suffix and s.endswith(suffix):
            return s[: len(s) - len(suffix)]
        return s

    @staticmethod
    def remove_suffix_ignore_case(s: str | None, suffix: str) -> str:
        """忽略大小写移除后缀。"""
        if s is None:
            return ""
        if suffix and s[-len(suffix) :].lower() == suffix.lower():
            return s[: len(s) - len(suffix)]
        return s

    # ------------------------------------------------------------------
    # 首字母大小写
    # ------------------------------------------------------------------
    @staticmethod
    def upper_first(s: str | None) -> str:
        """将首字母大写，其余保持不变。"""
        if s is None or not s:
            return ""
        return s[0].upper() + s[1:]

    @staticmethod
    def lower_first(s: str | None) -> str:
        """将首字母小写，其余保持不变。"""
        if s is None or not s:
            return ""
        return s[0].lower() + s[1:]

    # ------------------------------------------------------------------
    # 命名风格转换
    # ------------------------------------------------------------------
    @staticmethod
    def to_underline_case(s: str | None) -> str:
        """驼峰转下划线：``camelCase`` → ``camel_case``。

        连续大写字母视为整体（如 ``HTTPSConnection`` → ``https_connection``）。
        """
        if s is None or not s:
            return ""
        # 1) 小写/数字 -> 大写 边界处插入下划线：camelC -> camel_C
        result = re.sub(r"(?<=[a-z0-9])([A-Z])", r"_\1", s)
        # 2) 连续大写后接 大写+小写 时拆分：HTTPSConnection -> HTTPS_Connection
        result = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", result)
        return result.lower()

    @staticmethod
    def to_camel_case(s: str | None) -> str:
        """下划线转驼峰：``under_score_case`` → ``underScoreCase``。"""
        if s is None or not s:
            return ""
        s = s.lower()
        return _UNDERLINE_BOUNDARY_RE.sub(lambda m: m.group(1).upper(), s)

    # ------------------------------------------------------------------
    # 比较
    # ------------------------------------------------------------------
    @staticmethod
    def equals(s1: str | None, s2: str | None) -> bool:
        """``null`` 安全的字符串相等判断。"""
        return s1 == s2

    @staticmethod
    def equals_ignore_case(s1: str | None, s2: str | None) -> bool:
        """``null`` 安全的忽略大小写相等判断。``None`` 仅与 ``None`` 相等。"""
        if s1 is None or s2 is None:
            return s1 is s2
        return s1.lower() == s2.lower()

    @staticmethod
    def contains(s: str | None, search: str) -> bool:
        """``null`` 安全的包含判断。"""
        if s is None:
            return False
        return search in s

    @staticmethod
    def contains_ignore_case(s: str | None, search: str) -> bool:
        """``null`` 安全的忽略大小写包含判断。"""
        if s is None:
            return False
        return search.lower() in s.lower()

    @staticmethod
    def startswith(s: str | None, prefix: str) -> bool:
        """``null`` 安全的前缀判断。"""
        if s is None:
            return False
        return s.startswith(prefix)

    @staticmethod
    def endswith(s: str | None, suffix: str) -> bool:
        """``null`` 安全的后缀判断。"""
        if s is None:
            return False
        return s.endswith(suffix)

    # ------------------------------------------------------------------
    # 重复 / 反转 / 裁剪
    # ------------------------------------------------------------------
    @staticmethod
    def repeat(s: str | None, n: int) -> str:
        """重复字符串 ``n`` 次。``n <= 0`` 返回空串。"""
        if s is None or n <= 0:
            return ""
        return s * n

    @staticmethod
    def reverse(s: str | None) -> str:
        """反转字符串。``None`` 返回空串。"""
        if s is None:
            return ""
        return s[::-1]

    @staticmethod
    def trim(s: str | None) -> str:
        """去除首尾空白。``None`` 返回空串。"""
        if s is None:
            return ""
        return s.strip()

    @staticmethod
    def clean_blank(s: str | None) -> str:
        """删除字符串中所有空白字符（包括内部空白）。"""
        if s is None:
            return ""
        return "".join(s.split())

    # ------------------------------------------------------------------
    # 字符类别判断
    # ------------------------------------------------------------------
    @staticmethod
    def is_numeric(s: str | None) -> bool:
        """判断是否仅由数字组成（允许前导负号，不允许空白）。"""
        if s is None or not s:
            return False
        try:
            float(s)
        except ValueError:
            return False
        return True

    @staticmethod
    def is_alpha(s: str | None) -> bool:
        """判断是否仅由字母组成。"""
        if s is None or not s:
            return False
        return s.isalpha()

    @staticmethod
    def is_upper(s: str | None) -> bool:
        """判断是否全为大写字母。

        与 Python ``str.isupper`` 的区别：数字、标点也视为不合法
        （与 Hutool ``StrUtil.isUpperCase`` 语义一致）。
        """
        if s is None or not s:
            return False
        return s.isalpha() and s.isupper()

    @staticmethod
    def is_lower(s: str | None) -> bool:
        """判断是否全为小写字母。

        与 Python ``str.islower`` 的区别：数字、标点也视为不合法
        （与 Hutool ``StrUtil.isLowerCase`` 语义一致）。
        """
        if s is None or not s:
            return False
        return s.isalpha() and s.islower()

    # ------------------------------------------------------------------
    # 填充
    # ------------------------------------------------------------------
    @staticmethod
    def fill(
        s: str | None,
        fill_char: str,
        length: int,
        is_prefix: bool = False,
    ) -> str:
        """用 ``fill_char`` 将字符串填充到 ``length`` 长度。

        Parameters
        ----------
        s:
            原字符串，``None`` 视为空串。
        fill_char:
            填充字符，必须长度为 1。
        length:
            目标总长度。
        is_prefix:
            ``True`` 在左侧填充（前缀），``False`` 在右侧填充（后缀）。
        """
        if len(fill_char) != 1:
            raise ValueError("fill_char 必须是单个字符")
        s = s or ""
        if length <= len(s):
            return s
        pad = fill_char * (length - len(s))
        return pad + s if is_prefix else s + pad

    # ------------------------------------------------------------------
    # 转换 / 拼接 / 分割
    # ------------------------------------------------------------------
    @staticmethod
    def concat(*parts: str | None) -> str:
        """拼接多个字符串，``None`` 视为空串。"""
        return "".join("" if p is None else p for p in parts)

    @staticmethod
    def split(s: str | None, separator: str, limit: int = -1) -> list[str]:
        """按分隔符分割字符串。

        Parameters
        ----------
        s:
            原字符串，``None`` 返回空列表。
        separator:
            分隔符。空字符串则按单字符切分。
        limit:
            最大分割份数，``-1`` 表示不限制。
        """
        if s is None:
            return []
        if separator == "":
            return list(s) if limit < 0 else list(s)[:limit]
        if limit < 0:
            return s.split(separator)
        if limit == 0:
            return []
        return s.split(separator, limit - 1)

    @staticmethod
    def join(iterable: Iterable[str | None], separator: str = "") -> str:
        """使用分隔符拼接可迭代对象，``None`` 元素跳过。"""
        return separator.join("" if x is None else x for x in iterable)

    # ------------------------------------------------------------------
    # UUID
    # ------------------------------------------------------------------
    @staticmethod
    def uuid(bare: bool = False) -> str:
        """生成随机 UUID 字符串。

        Parameters
        ----------
        bare:
            ``True`` 返回不带连字符的 32 位字符串。
        """
        value = str(_uuid.uuid4())
        return value.replace("-", "") if bare else value

    # ------------------------------------------------------------------
    # 对象转字符串（放最后，避免方法名 ``str`` 遮蔽内置 ``str`` 类型注解）
    # ------------------------------------------------------------------
    @staticmethod
    def str(obj: object | None) -> str:
        """将任意对象转为字符串。``None`` 返回空串。"""
        return "" if obj is None else str(obj)
