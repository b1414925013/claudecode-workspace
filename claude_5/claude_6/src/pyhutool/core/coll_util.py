"""集合工具。

对齐 Hutool 的 ``cn.hutool.core.util.CollUtil``。由于 Python 内置
``list`` / ``set`` / ``dict`` 已是首选容器，本工具不再提供 ``newArrayList``
等容器构造，而是聚焦于容器之上的通用操作（分页、分组、去重、扁平化等）。
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable
from typing import Any, TypeVar

__all__ = ["CollUtil"]

T = TypeVar("T")
K = TypeVar("K")


class CollUtil:
    """集合工具类，全部为静态方法。"""

    # ------------------------------------------------------------------
    # 空判断 / 大小
    # ------------------------------------------------------------------
    @staticmethod
    def is_empty(coll: Any) -> bool:
        """判断容器是否为空（``None`` 或长度为 0）。"""
        if coll is None:
            return True
        try:
            return len(coll) == 0
        except TypeError:
            return True

    @staticmethod
    def is_not_empty(coll: Any) -> bool:
        """判断容器是否非空。"""
        return not CollUtil.is_empty(coll)

    @staticmethod
    def size(coll: Any) -> int:
        """返回容器大小，``None`` 返回 0。"""
        if coll is None:
            return 0
        return len(coll)

    # ------------------------------------------------------------------
    # 查找
    # ------------------------------------------------------------------
    @staticmethod
    def contains(coll: Iterable[Any] | None, item: Any) -> bool:
        """``null`` 安全的包含判断。"""
        if coll is None:
            return False
        return any(x == item for x in coll)

    @staticmethod
    def first(coll: Iterable[T] | None, default: T | None = None) -> T | None:
        """返回第一个元素，空返回 ``default``。"""
        if coll is None:
            return default
        for x in coll:
            return x
        return default

    @staticmethod
    def last(seq: Iterable[T] | None, default: T | None = None) -> T | None:
        """返回最后一个元素。"""
        if seq is None:
            return default
        last_item: T | None = default
        for x in seq:
            last_item = x
        return last_item

    # ------------------------------------------------------------------
    # 变换
    # ------------------------------------------------------------------
    @staticmethod
    def reverse(seq: Iterable[T]) -> list[T]:
        """返回反转后的新列表（不修改原序列）。"""
        return list(seq)[::-1]

    @staticmethod
    def sort(
        seq: Iterable[Any],
        key: Callable[[Any], Any] | None = None,
        reverse: bool = False,
    ) -> list[Any]:
        """返回排序后的新列表。"""
        return sorted(seq, key=key, reverse=reverse)

    @staticmethod
    def distinct(seq: Iterable[T]) -> list[T]:
        """去重并保留首次出现顺序。"""
        seen: set[Any] = set()
        result: list[T] = []
        for x in seq:
            key = x
            if key not in seen:
                seen.add(key)
                result.append(x)
        return result

    @staticmethod
    def filter_(seq: Iterable[T], predicate: Callable[[T], bool]) -> list[T]:
        """过滤，返回新列表。命名为 ``filter_`` 避免遮蔽内置 ``filter``。"""
        return [x for x in seq if predicate(x)]

    @staticmethod
    def map_(seq: Iterable[T], func: Callable[[T], Any]) -> list[Any]:
        """映射，返回新列表。命名为 ``map_`` 避免遮蔽内置 ``map``。"""
        return [func(x) for x in seq]

    @staticmethod
    def flat_map(seq: Iterable[Iterable[T]]) -> list[T]:
        """扁平化一层嵌套序列。"""
        result: list[T] = []
        for sub in seq:
            result.extend(sub)
        return result

    @staticmethod
    def count(seq: Iterable[T], predicate: Callable[[T], bool] | None = None) -> int:
        """计数，``predicate`` 为 ``None`` 时返回元素总数。"""
        if predicate is None:
            return sum(1 for _ in seq)
        return sum(1 for x in seq if predicate(x))

    # ------------------------------------------------------------------
    # 分组 / 分页 / zip
    # ------------------------------------------------------------------
    @staticmethod
    def group_by(seq: Iterable[T], key_func: Callable[[T], K]) -> dict[K, list[T]]:
        """按键函数分组，返回 ``dict``。"""
        groups: dict[K, list[T]] = defaultdict(list)
        for x in seq:
            groups[key_func(x)].append(x)
        return dict(groups)

    @staticmethod
    def page(seq: Iterable[T], page_no: int, page_size: int) -> list[T]:
        """分页（1-based，与 Hutool ``PageUtil`` 一致）。"""
        if page_no < 1 or page_size < 1:
            return []
        items = list(seq)
        start = (page_no - 1) * page_size
        if start >= len(items):
            return []
        return items[start : start + page_size]

    @staticmethod
    def zip_(seq1: Iterable[Any], seq2: Iterable[Any]) -> list[tuple[Any, Any]]:
        """合并两个序列为元组列表，按较短的截断。"""
        return list(zip(seq1, seq2, strict=False))

    @staticmethod
    def join(seq: Iterable[Any], separator: str = "") -> str:
        """用分隔符拼接元素（元素转 ``str``）。"""
        return separator.join(str(x) for x in seq)

    # ------------------------------------------------------------------
    # 极值
    # ------------------------------------------------------------------
    @staticmethod
    def max(seq: Iterable[Any], default: Any = None) -> Any:
        """返回最大值，空序列返回 ``default``。"""
        items = list(seq)
        if not items:
            return default
        return max(items)

    @staticmethod
    def min(seq: Iterable[Any], default: Any = None) -> Any:
        """返回最小值，空序列返回 ``default``。"""
        items = list(seq)
        if not items:
            return default
        return min(items)

    # ------------------------------------------------------------------
    # 集合运算
    # ------------------------------------------------------------------
    @staticmethod
    def union(seq1: Iterable[T], seq2: Iterable[T]) -> list[T]:
        """并集（保留顺序去重）。"""
        return CollUtil.distinct(list(seq1) + list(seq2))

    @staticmethod
    def intersect(seq1: Iterable[T], seq2: Iterable[T]) -> list[T]:
        """交集（保留 seq1 顺序）。"""
        s2: set[Any] = set(seq2)
        seen: set[Any] = set()
        result: list[T] = []
        for x in seq1:
            if x in s2 and x not in seen:
                seen.add(x)
                result.append(x)
        return result

    @staticmethod
    def subtract(seq1: Iterable[T], seq2: Iterable[T]) -> list[T]:
        """差集：seq1 中不在 seq2 的元素（保留顺序去重）。"""
        s2: set[Any] = set(seq2)
        seen: set[Any] = set()
        result: list[T] = []
        for x in seq1:
            if x not in s2 and x not in seen:
                seen.add(x)
                result.append(x)
        return result
