"""RegexUtil 单元测试。"""

from __future__ import annotations

import re

from pyhutool.core import RegexUtil


class TestMatch:
    """匹配。"""

    def test_is_match(self) -> None:
        assert RegexUtil.is_match(r"\d+", "12345") is True
        assert RegexUtil.is_match(r"\d+", "12a45") is False  # 完全匹配

    def test_is_contains(self) -> None:
        assert RegexUtil.is_contains(r"\d+", "ab12cd") is True
        assert RegexUtil.is_contains(r"\d+", "abcd") is False


class TestFind:
    """查找。"""

    def test_find_first(self) -> None:
        assert RegexUtil.find_first(r"\d+", "ab12cd34") == "12"
        assert RegexUtil.find_first(r"\d+", "abc") is None

    def test_find_group(self) -> None:
        assert RegexUtil.find_group(r"(\d+)-(\d+)", "12-34", 1) == "12"
        assert RegexUtil.find_group(r"(\d+)-(\d+)", "12-34", 2) == "34"
        assert RegexUtil.find_group(r"(\d+)", "abc", 1) is None

    def test_find_group_out_of_range(self) -> None:
        assert RegexUtil.find_group(r"(\d+)", "123", 5) is None

    def test_find_all(self) -> None:
        assert RegexUtil.find_all(r"\d+", "a1b22c333") == ["1", "22", "333"]

    def test_find_all_group(self) -> None:
        assert RegexUtil.find_all_group(r"(\d+)-(\d+)", "1-2 and 3-4", 1) == ["1", "3"]


class TestExtract:
    """提取别名。"""

    def test_extract(self) -> None:
        assert RegexUtil.extract(r"user:(\w+)", "user:tom") == "tom"
        assert RegexUtil.extract(r"user:(\w+)", "no match") is None

    def test_extract_all(self) -> None:
        assert RegexUtil.extract_all(r"id=(\d+)", "id=1,id=2") == ["1", "2"]


class TestReplace:
    """替换 / 删除。"""

    def test_replace_all(self) -> None:
        assert RegexUtil.replace_all(r"\d+", "a1b2", "X") == "aXbX"

    def test_replace_first(self) -> None:
        assert RegexUtil.replace_first(r"\d+", "a1b2", "X") == "aXb2"

    def test_del_first(self) -> None:
        assert RegexUtil.del_first(r"\d+", "a1b2") == "ab2"

    def test_del_all(self) -> None:
        assert RegexUtil.del_all(r"\d+", "a1b2") == "ab"


class TestCount:
    """计数。"""

    def test_count(self) -> None:
        assert RegexUtil.count(r"\d", "a1b2c3") == 3
        assert RegexUtil.count(r"z", "abc") == 0


class TestSplit:
    """分割。"""

    def test_split(self) -> None:
        assert RegexUtil.split(r"[,\s]+", "a, b c") == ["a", "b", "c"]

    def test_split_with_limit(self) -> None:
        assert RegexUtil.split(r",", "a,b,c", 2) == ["a", "b", "c"]


class TestReplaceFunc:
    """回调替换。"""

    def test_replace_func(self) -> None:
        result = RegexUtil.replace_func(r"\d+", "a1b2", lambda m: str(int(m.group()) * 2))
        assert result == "a2b4"


def test_compile_pattern_acceptable() -> None:
    """接受预编译 Pattern。"""
    pat = re.compile(r"\d+")
    assert RegexUtil.is_match(pat, "123") is True
    assert RegexUtil.find_first(pat, "a1") == "1"
