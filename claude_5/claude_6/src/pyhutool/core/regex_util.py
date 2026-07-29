"""正则工具。

对齐 Hutool 的 ``cn.hutool.core.util.ReUtil`` 与 ``cn.hutool.core.re.ReUtil``，
提供匹配、查找、替换、删除等正则操作。
"""

from __future__ import annotations

import re
from collections.abc import Callable
from re import Pattern

__all__ = ["RegexUtil"]


def _compile(pattern: str | Pattern[str], flags: int = 0) -> Pattern[str]:
    """编译正则，已经是 Pattern 则原样返回。"""
    if isinstance(pattern, Pattern):
        return pattern
    return re.compile(pattern, flags)


class RegexUtil:
    """正则工具类，全部为静态方法。"""

    # ------------------------------------------------------------------
    # 匹配
    # ------------------------------------------------------------------
    @staticmethod
    def is_match(pattern: str | Pattern[str], value: str) -> bool:
        """判断整个字符串是否完全匹配（对应 Hutool ``ReUtil.isMatch``）。"""
        return _compile(pattern).fullmatch(value) is not None

    @staticmethod
    def is_contains(pattern: str | Pattern[str], value: str) -> bool:
        """判断是否包含匹配（搜索）。"""
        return _compile(pattern).search(value) is not None

    # ------------------------------------------------------------------
    # 查找
    # ------------------------------------------------------------------
    @staticmethod
    def find_first(pattern: str | Pattern[str], value: str) -> str | None:
        """返回第一个完整匹配的字符串，无匹配返回 ``None``。"""
        m = _compile(pattern).search(value)
        return m.group(0) if m else None

    @staticmethod
    def find_group(pattern: str | Pattern[str], value: str, group: int = 1) -> str | None:
        """返回第一个匹配的指定捕获组，无匹配返回 ``None``。"""
        m = _compile(pattern).search(value)
        if m is None:
            return None
        try:
            return m.group(group)
        except IndexError:
            return None

    @staticmethod
    def find_all(pattern: str | Pattern[str], value: str) -> list[str]:
        """返回所有完整匹配的字符串列表。"""
        return [m.group(0) for m in _compile(pattern).finditer(value)]

    @staticmethod
    def find_all_group(pattern: str | Pattern[str], value: str, group: int = 1) -> list[str]:
        """返回所有匹配中指定捕获组的列表。"""
        result: list[str] = []
        for m in _compile(pattern).finditer(value):
            try:
                g = m.group(group)
                if g is not None:
                    result.append(g)
            except IndexError:
                continue
        return result

    # ------------------------------------------------------------------
    # 提取（同 find_group，提供 Hutool 风格别名）
    # ------------------------------------------------------------------
    @staticmethod
    def extract(pattern: str | Pattern[str], value: str) -> str | None:
        """提取第一个捕获组（``group=1``）。"""
        return RegexUtil.find_group(pattern, value, 1)

    @staticmethod
    def extract_all(pattern: str | Pattern[str], value: str) -> list[str]:
        """提取所有匹配的第一个捕获组。"""
        return RegexUtil.find_all_group(pattern, value, 1)

    # ------------------------------------------------------------------
    # 替换 / 删除
    # ------------------------------------------------------------------
    @staticmethod
    def replace_all(pattern: str | Pattern[str], value: str, replacement: str) -> str:
        """替换所有匹配。"""
        return _compile(pattern).sub(replacement, value)

    @staticmethod
    def replace_first(pattern: str | Pattern[str], value: str, replacement: str) -> str:
        """替换第一个匹配。"""
        return _compile(pattern).sub(replacement, value, count=1)

    @staticmethod
    def del_first(pattern: str | Pattern[str], value: str) -> str:
        """删除第一个匹配。"""
        return _compile(pattern).sub("", value, count=1)

    @staticmethod
    def del_all(pattern: str | Pattern[str], value: str) -> str:
        """删除所有匹配。"""
        return _compile(pattern).sub("", value)

    # ------------------------------------------------------------------
    # 计数
    # ------------------------------------------------------------------
    @staticmethod
    def count(pattern: str | Pattern[str], value: str) -> int:
        """返回匹配次数。"""
        return sum(1 for _ in _compile(pattern).finditer(value))

    # ------------------------------------------------------------------
    # 分割
    # ------------------------------------------------------------------
    @staticmethod
    def split(pattern: str | Pattern[str], value: str, limit: int = 0) -> list[str]:
        """按正则分割字符串。"""
        return _compile(pattern).split(value, maxsplit=0 if limit < 0 else limit)

    # ------------------------------------------------------------------
    # 替换为函数
    # ------------------------------------------------------------------
    @staticmethod
    def replace_func(
        pattern: str | Pattern[str],
        value: str,
        func: Callable[[re.Match[str]], str],
    ) -> str:
        """使用回调函数替换匹配。"""
        return _compile(pattern).sub(func, value)
