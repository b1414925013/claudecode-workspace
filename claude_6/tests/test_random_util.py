"""RandomUtil 单元测试。"""

from __future__ import annotations

import re
import string

import pytest

from pyhutool.core import RandomUtil


class TestNumbers:
    """随机数。"""

    def test_random_int_range(self) -> None:
        for _ in range(100):
            n = RandomUtil.random_int(1, 10)
            assert 1 <= n < 10

    def test_random_int_invalid_range(self) -> None:
        with pytest.raises(ValueError):
            RandomUtil.random_int(10, 1)

    def test_random_int_with_range_closed(self) -> None:
        for _ in range(100):
            n = RandomUtil.random_int_with_range(1, 3)
            assert 1 <= n <= 3

    def test_random_double_range(self) -> None:
        for _ in range(100):
            n = RandomUtil.random_double(0, 1)
            assert 0 <= n < 1

    def test_random_double_invalid(self) -> None:
        with pytest.raises(ValueError):
            RandomUtil.random_double(1, 0)

    def test_random_boolean(self) -> None:
        results = {RandomUtil.random_boolean() for _ in range(50)}
        assert results <= {True, False}

    def test_random_char(self) -> None:
        c = RandomUtil.random_char("ABC")
        assert c in "ABC"
        with pytest.raises(ValueError):
            RandomUtil.random_char("")


class TestElements:
    """随机元素。"""

    def test_random_ele(self) -> None:
        seq = ["a", "b", "c"]
        for _ in range(50):
            assert RandomUtil.random_ele(seq) in seq

    def test_random_ele_empty(self) -> None:
        with pytest.raises(IndexError):
            RandomUtil.random_ele([])

    def test_random_els(self) -> None:
        seq = ["a", "b", "c"]
        result = RandomUtil.random_els(seq, 5)
        assert len(result) == 5
        for x in result:
            assert x in seq

    def test_random_els_zero(self) -> None:
        assert RandomUtil.random_els(["a"], 0) == []

    def test_random_els_distinct(self) -> None:
        result = RandomUtil.random_els_distinct([1, 2, 3, 4], 3)
        assert len(result) == 3
        assert len(set(result)) == 3

    def test_random_els_distinct_too_many(self) -> None:
        with pytest.raises(ValueError):
            RandomUtil.random_els_distinct([1, 2], 5)


class TestStrings:
    """随机字符串。"""

    def test_random_string(self) -> None:
        s = RandomUtil.random_string(10)
        assert len(s) == 10
        assert all(c in string.ascii_letters + string.digits for c in s)

    def test_random_string_zero(self) -> None:
        assert RandomUtil.random_string(0) == ""

    def test_random_numbers(self) -> None:
        s = RandomUtil.random_numbers(8)
        assert len(s) == 8
        assert s.isdigit()

    def test_random_lower_string(self) -> None:
        s = RandomUtil.random_lower_string(10)
        assert len(s) == 10
        assert s == s.lower()

    def test_random_upper_string(self) -> None:
        s = RandomUtil.random_upper_string(10)
        assert len(s) == 10


def test_seed_reproducible() -> None:
    """种子可复现。"""
    r1 = RandomUtil.seed(42)
    r2 = RandomUtil.seed(42)
    assert r1.randint(0, 1000) == r2.randint(0, 1000)


def test_random_numbers_format() -> None:
    """随机数字串符合预期格式。"""
    s = RandomUtil.random_numbers(4)
    assert re.fullmatch(r"\d{4}", s) is not None
