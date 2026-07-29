"""可变字符串构建器。

对齐 Hutool 的 ``cn.hutool.core.text.StrBuilder``。Python 标准库中字符串
本身不可变，``str.join`` 是高效拼接方式；本类提供链式 API 与
``StringBuilder`` 风格的语义，便于从 Java 迁移代码或对字符串进行
多次插入/删除操作。

底层使用 ``list[str]`` 累积片段，``to_string`` 时一次性 ``join``，
避免 O(n^2) 拷贝。
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Final

__all__ = ["StringBuilder"]

_NULL_STR: Final[str] = ""


def _to_str(value: Any) -> str:
    """将任意值转为字符串。``None`` 返回空串。"""
    if value is None:
        return _NULL_STR
    if isinstance(value, str):
        return value
    return str(value)


class StringBuilder:
    """可变字符串构建器。

    Examples
    --------
    >>> sb = StringBuilder("Hello")
    >>> sb.append(", ").append("World").append_line()
    >>> sb.insert(5, "!")
    >>> sb.to_string()
    'Hello!, World\\n'
    """

    def __init__(self, init: str | Iterable[Any] | None = None) -> None:
        """初始化构建器。"""
        self._parts: list[str] = []
        if init is None:
            return
        if isinstance(init, str):
            if init:
                self._parts.append(init)
        else:
            for x in init:
                self.append(x)

    # ------------------------------------------------------------------
    # 追加
    # ------------------------------------------------------------------
    def append(self, value: Any) -> StringBuilder:
        """追加内容。返回 ``self`` 以便链式调用。"""
        self._parts.append(_to_str(value))
        return self

    def append_line(self, value: Any | None = None) -> StringBuilder:
        """追加内容并换行。

        ``value`` 为 ``None`` 时仅追加一个换行符。
        """
        if value is not None:
            self._parts.append(_to_str(value))
        self._parts.append("\n")
        return self

    def append_lines(self, values: Iterable[Any]) -> StringBuilder:
        """逐行追加多个值（每个值后追加换行）。"""
        for v in values:
            self.append_line(v)
        return self

    # ------------------------------------------------------------------
    # 插入 / 删除
    # ------------------------------------------------------------------
    def insert(self, index: int, value: Any) -> StringBuilder:
        """在指定位置插入内容。``index`` 超出范围则按 ``append`` 处理。"""
        text = _to_str(value)
        if not text:
            return self
        # 把当前拼接展开为字符串再插入
        current = self.to_string()
        if index < 0:
            index = max(0, len(current) + index)
        if index >= len(current):
            self._parts = [current, text]
        else:
            self._parts = [current[:index], text, current[index:]]
        return self

    def delete(self, start: int, end: int) -> StringBuilder:
        """删除 ``[start, end)`` 范围内的字符。"""
        current = self.to_string()
        n = len(current)
        start = max(0, start)
        end = min(n, end)
        if start >= end:
            return self
        self._parts = [current[:start], current[end:]]
        return self

    def delete_char_at(self, index: int) -> StringBuilder:
        """删除指定位置的字符。"""
        return self.delete(index, index + 1)

    # ------------------------------------------------------------------
    # 修改
    # ------------------------------------------------------------------
    def replace(self, start: int, end: int, value: Any) -> StringBuilder:
        """替换 ``[start, end)`` 范围内的字符为 ``value``。"""
        current = self.to_string()
        n = len(current)
        start = max(0, start)
        end = min(n, end)
        if start > end:
            end = start
        text = _to_str(value)
        self._parts = [current[:start], text, current[end:]]
        return self

    def reverse(self) -> StringBuilder:
        """反转当前所有字符。"""
        self._parts = [self.to_string()[::-1]]
        return self

    def clear(self) -> StringBuilder:
        """清空内容。"""
        self._parts.clear()
        return self

    # ------------------------------------------------------------------
    # 查询
    # ------------------------------------------------------------------
    def length(self) -> int:
        """返回当前字符串长度。"""
        return sum(len(p) for p in self._parts)

    def is_empty(self) -> bool:
        """返回是否为空。"""
        return self.length() == 0

    def char_at(self, index: int) -> str:
        """返回 ``index`` 处的字符（长度 1 的字符串）。"""
        return self.to_string()[index]

    def index_of(self, sub: str, start: int = 0) -> int:
        """查找子串首次出现位置，未找到返回 -1。"""
        return self.to_string().find(sub, start)

    # ------------------------------------------------------------------
    # 输出
    # ------------------------------------------------------------------
    def to_string(self) -> str:
        """拼接为字符串。"""
        return "".join(self._parts)

    def __str__(self) -> str:
        """返回当前拼接结果。"""
        return self.to_string()

    def __len__(self) -> int:
        """返回字符串长度。"""
        return self.length()

    def __eq__(self, other: object) -> bool:
        """与字符串或其他 ``StringBuilder`` 比较内容是否相等。"""
        if isinstance(other, StringBuilder):
            return self.to_string() == other.to_string()
        if isinstance(other, str):
            return self.to_string() == other
        return NotImplemented

    def __repr__(self) -> str:
        """返回 ``StringBuilder`` 的可打印表示。"""
        return f"StringBuilder({self.to_string()!r})"

    def __iter__(self) -> Iterable[str]:
        """迭代字符。"""
        return iter(self.to_string())
