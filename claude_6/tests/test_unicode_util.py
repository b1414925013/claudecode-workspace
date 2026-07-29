"""UnicodeUtil 单元测试。"""

from __future__ import annotations

from pyhutool.text import UnicodeUtil


class TestToUnicode:
    """转义为 \\uXXXX。"""

    def test_ascii_unchanged(self) -> None:
        assert UnicodeUtil.to_unicode("Hello, World!") == "Hello, World!"

    def test_chinese(self) -> None:
        # 你 = U+4F60, 好 = U+597D
        assert UnicodeUtil.to_unicode("你好") == "\\u4f60\\u597d"

    def test_mixed(self) -> None:
        assert UnicodeUtil.to_unicode("a你b") == "a\\u4f60b"

    def test_none(self) -> None:
        assert UnicodeUtil.to_unicode(None) == ""

    def test_empty(self) -> None:
        assert UnicodeUtil.to_unicode("") == ""

    def test_uppercase_hex(self) -> None:
        # 实现使用 04x，故输出小写
        result = UnicodeUtil.to_unicode("中")
        assert result == "\\u4e2d"

    def test_emoji_uses_surrogate_pair(self) -> None:
        # 😀 = U+1F600 → 代理对 D83D DE00
        result = UnicodeUtil.to_unicode("😀")
        assert result == "\\ud83d\\ude00"

    def test_escape_alias(self) -> None:
        assert UnicodeUtil.escape("你") == UnicodeUtil.to_unicode("你")


class TestToString:
    """从 \\uXXXX 解码。"""

    def test_ascii_only(self) -> None:
        assert UnicodeUtil.to_string("Hello") == "Hello"

    def test_chinese(self) -> None:
        assert UnicodeUtil.to_string("\\u4f60\\u597d") == "你好"

    def test_mixed(self) -> None:
        assert UnicodeUtil.to_string("a\\u4f60b") == "a你b"

    def test_none(self) -> None:
        assert UnicodeUtil.to_string(None) == ""

    def test_empty(self) -> None:
        assert UnicodeUtil.to_string("") == ""

    def test_uppercase_hex(self) -> None:
        assert UnicodeUtil.to_string("\\u4F60\\u597D") == "你好"

    def test_surrogate_pair(self) -> None:
        # 😀
        assert UnicodeUtil.to_string("\\ud83d\\ude00") == "😀"

    def test_unescape_alias(self) -> None:
        assert UnicodeUtil.unescape("\\u4f60") == "你"

    def test_no_escape_kept(self) -> None:
        # 没有转义序列的原样返回
        assert UnicodeUtil.to_string("plain text") == "plain text"

    def test_invalid_escape_kept(self) -> None:
        # 长度不对的转义不匹配，原样返回
        assert UnicodeUtil.to_string("\\u12") == "\\u12"


class TestRoundtrip:
    """往返转换。"""

    def test_roundtrip_chinese(self) -> None:
        original = "你好，世界！"
        assert UnicodeUtil.to_string(UnicodeUtil.to_unicode(original)) == original

    def test_roundtrip_mixed(self) -> None:
        original = "Hello, 你好，😀 emoji"
        encoded = UnicodeUtil.to_unicode(original)
        assert UnicodeUtil.to_string(encoded) == original
