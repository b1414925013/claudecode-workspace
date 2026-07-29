"""StrUtil 单元测试。"""

from __future__ import annotations

import re

import pytest

from pyhutool.core import StrUtil
from pyhutool.core.exceptions import UtilError


class TestBlankCheck:
    """空值判断。"""

    def test_is_blank_none(self) -> None:
        assert StrUtil.is_blank(None) is True

    def test_is_blank_whitespace(self) -> None:
        assert StrUtil.is_blank("   ") is True
        assert StrUtil.is_blank("\t\n") is True

    def test_is_blank_normal(self) -> None:
        assert StrUtil.is_blank("a") is False

    def test_is_not_blank(self) -> None:
        assert StrUtil.is_not_blank(None) is False
        assert StrUtil.is_not_blank("a") is True

    def test_is_empty_none(self) -> None:
        assert StrUtil.is_empty(None) is True

    def test_is_empty_empty_string(self) -> None:
        assert StrUtil.is_empty("") is True
        assert StrUtil.is_empty(" ") is False  # 与 is_blank 区别

    def test_is_not_empty(self) -> None:
        assert StrUtil.is_not_empty("") is False
        assert StrUtil.is_not_empty(" ") is True


class TestDefaults:
    """空值替换。"""

    def test_blank_to_default(self) -> None:
        assert StrUtil.blank_to_default(None, "x") == "x"
        assert StrUtil.blank_to_default("  ", "x") == "x"
        assert StrUtil.blank_to_default("a", "x") == "a"

    def test_empty_to_default(self) -> None:
        assert StrUtil.empty_to_default(None, "x") == "x"
        assert StrUtil.empty_to_default("", "x") == "x"
        assert StrUtil.empty_to_default(" ", "x") == " "

    def test_null_to_default(self) -> None:
        assert StrUtil.null_to_default(None, "x") == "x"
        assert StrUtil.null_to_default("", "x") == ""
        assert StrUtil.null_to_default("a", "x") == "a"


class TestFormat:
    """格式化。"""

    def test_format_basic(self) -> None:
        assert StrUtil.format("hello {}", "world") == "hello world"
        assert StrUtil.format("{}-{}", 1, 2) == "1-2"

    def test_format_no_args(self) -> None:
        assert StrUtil.format("hello") == "hello"

    def test_format_none_pattern(self) -> None:
        assert StrUtil.format(None, "x") == ""

    def test_format_none_value(self) -> None:
        assert StrUtil.format("a={}", None) == "a="

    def test_format_more_placeholders_than_args(self) -> None:
        # 占位符多于参数时，剩余占位符保留
        assert StrUtil.format("{}-{}", 1) == "1-{}"

    def test_format_with_basic(self) -> None:
        assert StrUtil.format_with("a=?-b=?", "?", 1, 2) == "a=1-b=2"

    def test_format_with_none_pattern(self) -> None:
        assert StrUtil.format_with(None, "?", 1) == ""

    def test_format_with_none_value(self) -> None:
        assert StrUtil.format_with("a={}", "{}", None) == "a="

    def test_format_with_empty_placeholder_raises(self) -> None:
        with pytest.raises(ValueError):
            StrUtil.format_with("a", "", 1)


class TestSubAndPrefix:
    """截取与前后缀。"""

    def test_sub_pre_positive(self) -> None:
        assert StrUtil.sub_pre("hello", 3) == "hel"

    def test_sub_pre_negative(self) -> None:
        assert StrUtil.sub_pre("hello", -2) == "hel"

    def test_sub_pre_none(self) -> None:
        assert StrUtil.sub_pre(None, 3) == ""

    def test_sub_pre_negative_overflow(self) -> None:
        assert StrUtil.sub_pre("hi", -5) == "hi"

    def test_sub_suf(self) -> None:
        assert StrUtil.sub_suf("hello", 3) == "llo"

    def test_sub_suf_zero_or_none(self) -> None:
        assert StrUtil.sub_suf(None, 3) == ""
        assert StrUtil.sub_suf("hi", 0) == ""

    def test_sub_suf_overflow(self) -> None:
        assert StrUtil.sub_suf("hi", 10) == "hi"

    def test_remove_prefix(self) -> None:
        assert StrUtil.remove_prefix("helloWorld", "hello") == "World"
        assert StrUtil.remove_prefix("helloWorld", "Hi") == "helloWorld"
        assert StrUtil.remove_prefix(None, "x") == ""

    def test_remove_prefix_ignore_case(self) -> None:
        assert StrUtil.remove_prefix_ignore_case("HelloWorld", "hello") == "World"
        assert StrUtil.remove_prefix_ignore_case("helloWorld", "HELLO") == "World"
        assert StrUtil.remove_prefix_ignore_case(None, "hello") == ""
        assert StrUtil.remove_prefix_ignore_case("hello", "XYZ") == "hello"

    def test_remove_suffix(self) -> None:
        assert StrUtil.remove_suffix("hello.txt", ".txt") == "hello"
        assert StrUtil.remove_suffix("hello.txt", ".md") == "hello.txt"
        assert StrUtil.remove_suffix(None, "x") == ""

    def test_remove_suffix_ignore_case(self) -> None:
        assert StrUtil.remove_suffix_ignore_case("hello.TXT", ".txt") == "hello"
        assert StrUtil.remove_suffix_ignore_case(None, "x") == ""
        assert StrUtil.remove_suffix_ignore_case("hello.txt", ".MD") == "hello.txt"


class TestCaseConvert:
    """大小写与命名转换。"""

    def test_upper_first(self) -> None:
        assert StrUtil.upper_first("hello") == "Hello"
        assert StrUtil.upper_first("") == ""
        assert StrUtil.upper_first(None) == ""

    def test_lower_first(self) -> None:
        assert StrUtil.lower_first("Hello") == "hello"
        assert StrUtil.lower_first("") == ""
        assert StrUtil.lower_first(None) == ""

    def test_to_underline_case(self) -> None:
        assert StrUtil.to_underline_case("camelCase") == "camel_case"
        assert StrUtil.to_underline_case("HTTPSConnection") == "https_connection"
        assert StrUtil.to_underline_case("simple") == "simple"
        assert StrUtil.to_underline_case("") == ""
        assert StrUtil.to_underline_case(None) == ""

    def test_to_camel_case(self) -> None:
        assert StrUtil.to_camel_case("under_score_case") == "underScoreCase"
        assert StrUtil.to_camel_case("user_id") == "userId"
        assert StrUtil.to_camel_case("") == ""
        assert StrUtil.to_camel_case(None) == ""


class TestCompare:
    """比较。"""

    def test_equals(self) -> None:
        assert StrUtil.equals("a", "a") is True
        assert StrUtil.equals(None, None) is True
        assert StrUtil.equals("a", "b") is False

    def test_equals_ignore_case(self) -> None:
        assert StrUtil.equals_ignore_case("ABC", "abc") is True
        assert StrUtil.equals_ignore_case(None, None) is True
        assert StrUtil.equals_ignore_case(None, "a") is False
        assert StrUtil.equals_ignore_case("a", None) is False

    def test_contains(self) -> None:
        assert StrUtil.contains("hello", "ell") is True
        assert StrUtil.contains(None, "x") is False
        assert StrUtil.contains("hello", "x") is False

    def test_contains_ignore_case(self) -> None:
        assert StrUtil.contains_ignore_case("HELLO", "ell") is True
        assert StrUtil.contains_ignore_case(None, "x") is False

    def test_startswith(self) -> None:
        assert StrUtil.startswith("hello", "he") is True
        assert StrUtil.startswith(None, "he") is False

    def test_endswith(self) -> None:
        assert StrUtil.endswith("hello", "lo") is True
        assert StrUtil.endswith(None, "lo") is False


class TestRepeatReverseTrim:
    """重复 / 反转 / 裁剪。"""

    def test_repeat(self) -> None:
        assert StrUtil.repeat("ab", 3) == "ababab"
        assert StrUtil.repeat("ab", 0) == ""
        assert StrUtil.repeat(None, 3) == ""
        assert StrUtil.repeat("ab", -1) == ""

    def test_reverse(self) -> None:
        assert StrUtil.reverse("hello") == "olleh"
        assert StrUtil.reverse(None) == ""

    def test_trim(self) -> None:
        assert StrUtil.trim("  hi  ") == "hi"
        assert StrUtil.trim(None) == ""

    def test_clean_blank(self) -> None:
        assert StrUtil.clean_blank("  h e l l o  ") == "hello"
        assert StrUtil.clean_blank(None) == ""


class TestCategoryCheck:
    """字符类别判断。"""

    def test_is_numeric(self) -> None:
        assert StrUtil.is_numeric("123") is True
        assert StrUtil.is_numeric("-1.5") is True
        assert StrUtil.is_numeric("abc") is False
        assert StrUtil.is_numeric("") is False
        assert StrUtil.is_numeric(None) is False

    def test_is_alpha(self) -> None:
        assert StrUtil.is_alpha("abc") is True
        assert StrUtil.is_alpha("abc123") is False
        assert StrUtil.is_alpha("") is False
        assert StrUtil.is_alpha(None) is False

    def test_is_upper_lower(self) -> None:
        assert StrUtil.is_upper("ABC") is True
        assert StrUtil.is_upper("ABC1") is False
        assert StrUtil.is_upper("") is False
        assert StrUtil.is_lower("abc") is True
        assert StrUtil.is_lower("Abc") is False
        assert StrUtil.is_lower(None) is False


class TestFill:
    """填充。"""

    def test_fill_suffix(self) -> None:
        assert StrUtil.fill("ab", "0", 5) == "ab000"

    def test_fill_prefix(self) -> None:
        assert StrUtil.fill("ab", "0", 5, is_prefix=True) == "000ab"

    def test_fill_no_need(self) -> None:
        assert StrUtil.fill("hello", "0", 3) == "hello"

    def test_fill_none(self) -> None:
        assert StrUtil.fill(None, "0", 3) == "000"

    def test_fill_invalid_char(self) -> None:
        with pytest.raises(ValueError):
            StrUtil.fill("ab", "--", 5)


class TestConcatSplitJoin:
    """拼接 / 分割 / 连接。"""

    def test_str(self) -> None:
        assert StrUtil.str(None) == ""
        assert StrUtil.str(123) == "123"
        assert StrUtil.str([1, 2]) == "[1, 2]"

    def test_concat(self) -> None:
        assert StrUtil.concat("a", None, "b") == "ab"

    def test_split_normal(self) -> None:
        assert StrUtil.split("a,b,c", ",") == ["a", "b", "c"]

    def test_split_with_limit(self) -> None:
        assert StrUtil.split("a,b,c", ",", 2) == ["a", "b,c"]

    def test_split_limit_zero(self) -> None:
        assert StrUtil.split("a,b,c", ",", 0) == []

    def test_split_empty_separator(self) -> None:
        assert StrUtil.split("abc", "") == ["a", "b", "c"]

    def test_split_none(self) -> None:
        assert StrUtil.split(None, ",") == []

    def test_join(self) -> None:
        assert StrUtil.join(["a", None, "b"], "-") == "a--b"
        assert StrUtil.join(["a", "b"]) == "ab"


class TestUuid:
    """UUID。"""

    def test_uuid_default(self) -> None:
        value = StrUtil.uuid()
        assert re.fullmatch(r"[0-9a-f-]{36}", value) is not None

    def test_uuid_bare(self) -> None:
        value = StrUtil.uuid(bare=True)
        assert len(value) == 32
        assert "-" not in value

    def test_uuid_unique(self) -> None:
        assert StrUtil.uuid() != StrUtil.uuid()


def test_util_error_not_raised_in_normal_path() -> None:
    """占位：保证 UtilError 可被导入（覆盖导入路径）。"""
    assert issubclass(UtilError, Exception)
