"""JsonUtil 单元测试。"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

from pyhutool.core.exceptions import UtilError
from pyhutool.json import JsonUtil

# 模块级跳过：若环境未安装 orjson，所有用例跳过
orjson_available = True
try:
    import orjson  # noqa: F401
except ImportError:
    orjson_available = False

pytestmark = pytest.mark.skipif(not orjson_available, reason="需要 orjson")


class TestParse:
    """解析。"""

    def test_parse_object(self) -> None:
        result = JsonUtil.parse('{"a": 1, "b": "x"}')
        assert result == {"a": 1, "b": "x"}

    def test_parse_array(self) -> None:
        result = JsonUtil.parse("[1, 2, 3]")
        assert result == [1, 2, 3]

    def test_parse_scalars(self) -> None:
        assert JsonUtil.parse("42") == 42
        assert JsonUtil.parse("3.14") == 3.14
        assert JsonUtil.parse('"hello"') == "hello"
        assert JsonUtil.parse("true") is True
        assert JsonUtil.parse("false") is False
        assert JsonUtil.parse("null") is None

    def test_parse_bytes(self) -> None:
        result = JsonUtil.parse(b'{"x": 1}')
        assert result == {"x": 1}

    def test_parse_chinese_no_escape(self) -> None:
        # orjson 默认不转义非 ASCII
        result = JsonUtil.parse('{"name": "张三"}')
        assert result == {"name": "张三"}

    def test_parse_invalid_raises(self) -> None:
        with pytest.raises(UtilError):
            JsonUtil.parse("{not valid")

    def test_parse_obj_ok(self) -> None:
        result = JsonUtil.parse_obj('{"a": 1}')
        assert result == {"a": 1}

    def test_parse_obj_not_object_raises(self) -> None:
        with pytest.raises(UtilError):
            JsonUtil.parse_obj("[1, 2]")

    def test_parse_array_ok(self) -> None:
        result = JsonUtil.parse_array("[1, 2]")
        assert result == [1, 2]

    def test_parse_array_not_array_raises(self) -> None:
        with pytest.raises(UtilError):
            JsonUtil.parse_array('{"a": 1}')


class TestToJsonStr:
    """序列化。"""

    def test_basic_dict(self) -> None:
        assert JsonUtil.to_json_str({"a": 1}) == '{"a":1}'

    def test_list(self) -> None:
        assert JsonUtil.to_json_str([1, 2, 3]) == "[1,2,3]"

    def test_chinese_not_escaped(self) -> None:
        # orjson 默认不转义非 ASCII，与 Hutool 行为一致
        assert JsonUtil.to_json_str({"name": "张三"}) == '{"name":"张三"}'

    def test_indent(self) -> None:
        result = JsonUtil.to_json_str({"a": 1, "b": 2}, indent=2)
        assert "\n" in result
        assert '  "a": 1' in result

    def test_sort_keys(self) -> None:
        result = JsonUtil.to_json_str({"b": 1, "a": 2}, sort_keys=True)
        # 排序后 "a" 在前
        assert result.index('"a"') < result.index('"b"')

    def test_nested(self) -> None:
        data = {"list": [1, 2, {"k": "v"}], "null": None, "bool": True}
        text = JsonUtil.to_json_str(data)
        assert JsonUtil.parse(text) == data

    def test_datetime_native_support(self) -> None:
        from datetime import datetime

        dt = datetime(2026, 1, 15, 10, 30, 0)
        result = JsonUtil.to_json_str({"ts": dt})
        assert "2026-01-15" in result
        assert "10:30:00" in result

    def test_decimal_native_support(self) -> None:
        from decimal import Decimal

        result = JsonUtil.to_json_str({"v": Decimal("3.14")})
        assert "3.14" in result

    def test_custom_object_fallback(self) -> None:
        class User:
            def __init__(self) -> None:
                self.name = "alice"

        result = JsonUtil.to_json_str(User())
        assert '"name":"alice"' in result

    def test_serialize_unsupported_raises(self) -> None:
        # 自定义类无 __dict__ 也无法转换时（如裸 object）
        result = JsonUtil.to_json_str(object())
        # 走 default 钩子转 str，不会抛错
        assert isinstance(result, str)


class TestPrettyFormat:
    """美化。"""

    def test_pretty_format_from_compact(self) -> None:
        compact = '{"a":1,"b":[1,2]}'
        result = JsonUtil.pretty_format(compact)
        assert "\n" in result
        assert "  " in result  # 缩进

    def test_pretty_format_idempotent(self) -> None:
        text = '{"a": 1}'
        result = JsonUtil.pretty_format(text)
        # 二次美化应保持稳定
        assert JsonUtil.pretty_format(result) == result


class TestFileIO:
    """文件读写。"""

    def test_write_then_read(self, tmp_path: Path) -> None:
        f = tmp_path / "data.json"
        data = {"name": "alice", "age": 30, "tags": ["a", "b"]}
        JsonUtil.write_json_file(data, f)
        assert f.exists()

        result = JsonUtil.read_json_file(f)
        assert result == data

    def test_write_with_indent(self, tmp_path: Path) -> None:
        f = tmp_path / "data.json"
        JsonUtil.write_json_file({"a": 1}, f, indent=2)
        content = f.read_text(encoding="utf-8")
        assert "\n" in content
        assert "  " in content

    def test_write_append(self, tmp_path: Path) -> None:
        f = tmp_path / "data.json"
        JsonUtil.write_json_file({"a": 1}, f)
        JsonUtil.write_json_file({"b": 2}, f, append=True)
        content = f.read_text(encoding="utf-8")
        # 第二段 JSON 紧跟第一段，整体仍是字符串
        assert '"a":1' in content
        assert '"b":2' in content

    def test_read_missing_raises(self, tmp_path: Path) -> None:
        # FileUtil 的 read_string 会抛 FileNotFoundError → 转为读取错误
        with pytest.raises((UtilError, FileNotFoundError, OSError)):
            JsonUtil.read_json_file(tmp_path / "missing.json")


class TestIsJson:
    """类型判断。"""

    def test_is_json_object_true(self) -> None:
        assert JsonUtil.is_json('{"a": 1}') is True

    def test_is_json_array_true(self) -> None:
        assert JsonUtil.is_json("[1, 2, 3]") is True

    def test_is_json_scalar_false(self) -> None:
        # 标量不算合法 JSON（与 Hutool 行为一致）
        assert JsonUtil.is_json("42") is False
        assert JsonUtil.is_json('"hello"') is False
        assert JsonUtil.is_json("true") is False

    def test_is_json_invalid_false(self) -> None:
        assert JsonUtil.is_json("not json") is False
        assert JsonUtil.is_json("{missing}") is False

    def test_is_json_none_empty_false(self) -> None:
        assert JsonUtil.is_json(None) is False
        assert JsonUtil.is_json("") is False

    def test_is_json_object_only(self) -> None:
        assert JsonUtil.is_json_object('{"a": 1}') is True
        assert JsonUtil.is_json_object("[1, 2]") is False

    def test_is_json_array_only(self) -> None:
        assert JsonUtil.is_json_array("[1, 2]") is True
        assert JsonUtil.is_json_array('{"a": 1}') is False


class TestEscape:
    """转义。"""

    def test_escape_quotes(self) -> None:
        assert JsonUtil.escape('hello "world"') == 'hello \\"world\\"'

    def test_escape_backslash(self) -> None:
        assert JsonUtil.escape("a\\b") == "a\\\\b"

    def test_escape_newline(self) -> None:
        assert JsonUtil.escape("a\nb") == "a\\nb"

    def test_escape_tab(self) -> None:
        assert JsonUtil.escape("a\tb") == "a\\tb"

    def test_escape_carriage_return(self) -> None:
        assert JsonUtil.escape("a\rb") == "a\\rb"

    def test_escape_backspace_formfeed(self) -> None:
        assert JsonUtil.escape("a\bb") == "a\\bb"
        assert JsonUtil.escape("a\fb") == "a\\fb"

    def test_escape_control_chars(self) -> None:
        # 0x00 NUL 应转为 \u0000
        assert JsonUtil.escape("\x00") == "\\u0000"
        # 0x1F 应转为 \u001f
        assert JsonUtil.escape("\x1f") == "\\u001f"

    def test_escape_none(self) -> None:
        assert JsonUtil.escape(None) == ""

    def test_escape_empty(self) -> None:
        assert JsonUtil.escape("") == ""

    def test_escape_normal_text(self) -> None:
        # 普通文本不变
        assert JsonUtil.escape("hello world") == "hello world"
        # 中文也不转义（与 Hutool 行为一致）
        assert JsonUtil.escape("你好") == "你好"


class TestUnescape:
    """反转义。"""

    def test_unescape_quotes(self) -> None:
        assert JsonUtil.unescape('hello \\"world\\"') == 'hello "world"'

    def test_unescape_backslash(self) -> None:
        assert JsonUtil.unescape("a\\\\b") == "a\\b"

    def test_unescape_newline(self) -> None:
        assert JsonUtil.unescape("a\\nb") == "a\nb"

    def test_unescape_tab(self) -> None:
        assert JsonUtil.unescape("a\\tb") == "a\tb"

    def test_unescape_carriage_return(self) -> None:
        assert JsonUtil.unescape("a\\rb") == "a\rb"

    def test_unescape_unicode(self) -> None:
        # 标准 JSON \uXXXX 形式
        assert JsonUtil.unescape("\\u4f60\\u597d") == "你好"

    def test_unescape_none(self) -> None:
        assert JsonUtil.unescape(None) == ""

    def test_unescape_empty(self) -> None:
        assert JsonUtil.unescape("") == ""

    def test_unescape_plain(self) -> None:
        assert JsonUtil.unescape("hello world") == "hello world"

    def test_roundtrip_escape_unescape(self) -> None:
        original = 'hello "world", \\ path \n newline \t tab'
        escaped = JsonUtil.escape(original)
        assert JsonUtil.unescape(escaped) == original

    def test_unescape_invalid_raises(self) -> None:
        # 包含非法转义序列
        with pytest.raises(UtilError):
            JsonUtil.unescape("\\xinvalid")


class TestQuote:
    """quote。"""

    def test_quote_normal(self) -> None:
        assert JsonUtil.quote("hello") == '"hello"'

    def test_quote_with_escape(self) -> None:
        assert JsonUtil.quote('a"b') == '"a\\"b"'

    def test_quote_with_newline(self) -> None:
        assert JsonUtil.quote("a\nb") == '"a\\nb"'

    def test_quote_none(self) -> None:
        assert JsonUtil.quote(None) == "null"

    def test_quote_empty(self) -> None:
        assert JsonUtil.quote("") == '""'

    def test_quote_chinese(self) -> None:
        # 中文不转义，只加引号
        assert JsonUtil.quote("你好") == '"你好"'


class TestMissingDependency:
    """模拟 orjson 未安装场景。"""

    def test_parse_without_orjson_raises_util_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # 让 _require_orjson 视为缺失
        import pyhutool.json.json_util as mod

        monkeypatch.setattr(
            mod,
            "_require_orjson",
            _raise_import_error,
        )
        with pytest.raises(UtilError) as excinfo:
            JsonUtil.parse("{}")
        assert "pyhutool[json]" in str(excinfo.value)


def _raise_import_error() -> Any:
    """用于 monkeypatch，模拟 orjson 未安装：抛 ``UtilError`` 与真实路径一致。"""
    raise UtilError(
        "pyhutool.json 需要 orjson 支持，请运行：pip install 'pyhutool[json]'",
        cause=ImportError("simulated: orjson not installed"),
    )


# 清理：测试结束时确保 sys.modules 中没有遗留 orjson 缓存影响其他用例
def teardown_module() -> None:
    sys.modules.pop("orjson", None)
