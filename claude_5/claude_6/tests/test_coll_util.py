"""CollUtil 单元测试。"""

from __future__ import annotations

from pyhutool.core import CollUtil


class TestEmpty:
    """空判断 / 大小。"""

    def test_is_empty(self) -> None:
        assert CollUtil.is_empty(None) is True
        assert CollUtil.is_empty([]) is True
        assert CollUtil.is_empty({}) is True
        assert CollUtil.is_empty([1]) is False

    def test_is_empty_non_iterable(self) -> None:
        # 没有 len 的对象视为空
        assert CollUtil.is_empty(123) is True

    def test_is_not_empty(self) -> None:
        assert CollUtil.is_not_empty([1]) is True
        assert CollUtil.is_not_empty(None) is False

    def test_size(self) -> None:
        assert CollUtil.size(None) == 0
        assert CollUtil.size([1, 2, 3]) == 3


class TestFind:
    """查找。"""

    def test_contains(self) -> None:
        assert CollUtil.contains([1, 2, 3], 2) is True
        assert CollUtil.contains(None, 2) is False
        assert CollUtil.contains([1, 2, 3], 9) is False

    def test_first(self) -> None:
        assert CollUtil.first([1, 2, 3]) == 1
        assert CollUtil.first([]) is None
        assert CollUtil.first(None, "x") == "x"

    def test_last(self) -> None:
        assert CollUtil.last([1, 2, 3]) == 3
        assert CollUtil.last([]) is None
        assert CollUtil.last(None, "x") == "x"


class TestTransform:
    """变换。"""

    def test_reverse(self) -> None:
        assert CollUtil.reverse([1, 2, 3]) == [3, 2, 1]
        assert CollUtil.reverse((1, 2)) == [2, 1]

    def test_sort(self) -> None:
        assert CollUtil.sort([3, 1, 2]) == [1, 2, 3]
        assert CollUtil.sort([3, 1, 2], reverse=True) == [3, 2, 1]
        assert CollUtil.sort(["b", "a"]) == ["a", "b"]

    def test_distinct(self) -> None:
        assert CollUtil.distinct([1, 2, 2, 3, 1]) == [1, 2, 3]

    def test_filter_(self) -> None:
        assert CollUtil.filter_([1, 2, 3, 4], lambda x: x % 2 == 0) == [2, 4]

    def test_map_(self) -> None:
        assert CollUtil.map_([1, 2, 3], lambda x: x * 2) == [2, 4, 6]

    def test_flat_map(self) -> None:
        assert CollUtil.flat_map([[1, 2], [3, 4]]) == [1, 2, 3, 4]

    def test_count(self) -> None:
        assert CollUtil.count([1, 2, 3]) == 3
        assert CollUtil.count([1, 2, 3, 4], lambda x: x % 2 == 0) == 2


class TestGroupPage:
    """分组 / 分页 / zip。"""

    def test_group_by(self) -> None:
        groups = CollUtil.group_by([1, 2, 3, 4, 5], lambda x: x % 2)
        assert groups[0] == [2, 4]
        assert groups[1] == [1, 3, 5]

    def test_page(self) -> None:
        assert CollUtil.page([1, 2, 3, 4, 5], 1, 2) == [1, 2]
        assert CollUtil.page([1, 2, 3, 4, 5], 2, 2) == [3, 4]
        assert CollUtil.page([1, 2, 3, 4, 5], 3, 2) == [5]
        assert CollUtil.page([1, 2, 3, 4, 5], 4, 2) == []
        assert CollUtil.page([1, 2, 3], 0, 2) == []

    def test_zip_(self) -> None:
        assert CollUtil.zip_([1, 2, 3], ["a", "b"]) == [(1, "a"), (2, "b")]

    def test_join(self) -> None:
        assert CollUtil.join([1, 2, 3], "-") == "1-2-3"
        assert CollUtil.join([1, 2, 3]) == "123"


class TestExtremum:
    """极值。"""

    def test_max_min(self) -> None:
        assert CollUtil.max([3, 1, 2]) == 3
        assert CollUtil.min([3, 1, 2]) == 1
        assert CollUtil.max([]) is None


class TestSetOps:
    """集合运算。"""

    def test_union(self) -> None:
        assert CollUtil.union([1, 2, 3], [2, 3, 4]) == [1, 2, 3, 4]

    def test_intersect(self) -> None:
        assert CollUtil.intersect([1, 2, 3], [2, 3, 4]) == [2, 3]

    def test_subtract(self) -> None:
        assert CollUtil.subtract([1, 2, 3], [2]) == [1, 3]
