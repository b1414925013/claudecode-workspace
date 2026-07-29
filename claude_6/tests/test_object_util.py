"""ObjectUtil 单元测试。"""

from __future__ import annotations

import pytest

from pyhutool.core import ObjectUtil


class TestNullCheck:
    """null 判断与默认值。"""

    def test_is_null(self) -> None:
        assert ObjectUtil.is_null(None) is True
        assert ObjectUtil.is_null(0) is False
        assert ObjectUtil.is_null("") is False

    def test_is_not_null(self) -> None:
        assert ObjectUtil.is_not_null(None) is False
        assert ObjectUtil.is_not_null(0) is True

    def test_default_if_null(self) -> None:
        assert ObjectUtil.default_if_null(None, "x") == "x"
        assert ObjectUtil.default_if_null("a", "x") == "a"


class TestEqualAndHash:
    """判等与哈希。"""

    def test_equal(self) -> None:
        assert ObjectUtil.equal("a", "a") is True
        assert ObjectUtil.equal(None, None) is True
        assert ObjectUtil.equal(1, 1) is True
        assert ObjectUtil.equal([1], [1]) is True
        assert ObjectUtil.equal("a", "b") is False

    def test_hash_code(self) -> None:
        assert ObjectUtil.hash_code(None) == 0
        assert ObjectUtil.hash_code("a") == hash("a")

    def test_to_string(self) -> None:
        assert ObjectUtil.to_string(None) == ""
        assert ObjectUtil.to_string(123) == "123"


class TestEmptyCheck:
    """空判断。"""

    def test_is_empty_none(self) -> None:
        assert ObjectUtil.is_empty(None) is True

    def test_is_empty_str(self) -> None:
        assert ObjectUtil.is_empty("") is True
        assert ObjectUtil.is_empty(" ") is False

    def test_is_empty_collection(self) -> None:
        assert ObjectUtil.is_empty([]) is True
        assert ObjectUtil.is_empty([1]) is False
        assert ObjectUtil.is_empty({}) is True
        assert ObjectUtil.is_empty({"a": 1}) is False

    def test_is_empty_other(self) -> None:
        # 非 Sized 对象视为非空
        assert ObjectUtil.is_empty(0) is False

    def test_is_not_empty(self) -> None:
        assert ObjectUtil.is_not_empty([]) is False
        assert ObjectUtil.is_not_empty([1]) is True


class TestBasicTypeAndClone:
    """基础类型与克隆。"""

    def test_is_basic_type(self) -> None:
        assert ObjectUtil.is_basic_type(None) is True
        assert ObjectUtil.is_basic_type(1) is True
        assert ObjectUtil.is_basic_type("a") is True
        assert ObjectUtil.is_basic_type((1, 2)) is True
        assert ObjectUtil.is_basic_type([1]) is False

    def test_clone_deep(self) -> None:
        original = {"a": [1, 2, {"b": 3}]}
        cloned = ObjectUtil.clone(original)
        assert cloned == original
        assert cloned is not original
        assert cloned["a"] is not original["a"]
        cloned["a"].append(99)
        assert original["a"] == [1, 2, {"b": 3}]


def test_demo() -> None:
    """占位以保证模块整体被执行。"""
    assert ObjectUtil.is_not_null(pytest)
