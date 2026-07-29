"""StringBuilder 单元测试。"""

from __future__ import annotations

from pyhutool.text import StringBuilder


class TestInit:
    """初始化。"""

    def test_init_empty(self) -> None:
        sb = StringBuilder()
        assert sb.is_empty() is True
        assert sb.length() == 0
        assert sb.to_string() == ""

    def test_init_with_str(self) -> None:
        sb = StringBuilder("hello")
        assert sb.to_string() == "hello"
        assert sb.length() == 5

    def test_init_with_iterable(self) -> None:
        sb = StringBuilder(["a", "b", "c"])
        assert sb.to_string() == "abc"

    def test_init_with_none(self) -> None:
        sb = StringBuilder(None)
        assert sb.is_empty() is True


class TestAppend:
    """追加。"""

    def test_append_str(self) -> None:
        sb = StringBuilder("a")
        result = sb.append("b").append("c")
        assert result is sb  # 链式
        assert sb.to_string() == "abc"

    def test_append_int(self) -> None:
        sb = StringBuilder()
        sb.append(42)
        assert sb.to_string() == "42"

    def test_append_none(self) -> None:
        sb = StringBuilder("a")
        sb.append(None)
        assert sb.to_string() == "a"

    def test_append_line_default(self) -> None:
        sb = StringBuilder()
        sb.append_line()
        assert sb.to_string() == "\n"

    def test_append_line_with_value(self) -> None:
        sb = StringBuilder()
        sb.append_line("hello")
        assert sb.to_string() == "hello\n"

    def test_append_lines(self) -> None:
        sb = StringBuilder()
        sb.append_lines(["a", "b", "c"])
        assert sb.to_string() == "a\nb\nc\n"


class TestInsertDelete:
    """插入 / 删除。"""

    def test_insert(self) -> None:
        sb = StringBuilder("HelloWorld")
        sb.insert(5, ", ")
        assert sb.to_string() == "Hello, World"

    def test_insert_at_end(self) -> None:
        sb = StringBuilder("abc")
        sb.insert(3, "d")
        assert sb.to_string() == "abcd"

    def test_insert_negative(self) -> None:
        sb = StringBuilder("abc")
        sb.insert(-1, "X")
        assert sb.to_string() == "abXc"

    def test_insert_empty_value(self) -> None:
        sb = StringBuilder("abc")
        sb.insert(1, "")
        assert sb.to_string() == "abc"

    def test_delete(self) -> None:
        sb = StringBuilder("Hello, World")
        sb.delete(5, 7)
        assert sb.to_string() == "HelloWorld"

    def test_delete_out_of_range(self) -> None:
        sb = StringBuilder("abc")
        sb.delete(10, 20)
        assert sb.to_string() == "abc"

    def test_delete_invalid_range(self) -> None:
        sb = StringBuilder("abc")
        sb.delete(2, 1)
        assert sb.to_string() == "abc"

    def test_delete_char_at(self) -> None:
        sb = StringBuilder("abc")
        sb.delete_char_at(1)
        assert sb.to_string() == "ac"


class TestModify:
    """修改。"""

    def test_replace(self) -> None:
        sb = StringBuilder("Hello, World")
        sb.replace(7, 12, "Python")
        assert sb.to_string() == "Hello, Python"

    def test_replace_at_end(self) -> None:
        sb = StringBuilder("abc")
        sb.replace(3, 3, "d")
        assert sb.to_string() == "abcd"

    def test_reverse(self) -> None:
        sb = StringBuilder("hello")
        sb.reverse()
        assert sb.to_string() == "olleh"

    def test_clear(self) -> None:
        sb = StringBuilder("hello")
        sb.clear()
        assert sb.is_empty() is True
        assert sb.to_string() == ""


class TestQuery:
    """查询。"""

    def test_length(self) -> None:
        sb = StringBuilder("héllo")  # é 是 1 字符
        assert sb.length() == 5

    def test_char_at(self) -> None:
        sb = StringBuilder("hello")
        assert sb.char_at(0) == "h"
        assert sb.char_at(4) == "o"

    def test_index_of(self) -> None:
        sb = StringBuilder("hello world")
        assert sb.index_of("world") == 6
        assert sb.index_of("xyz") == -1
        assert sb.index_of("l", 4) == 9

    def test_len_dunder(self) -> None:
        sb = StringBuilder("hello")
        assert len(sb) == 5


class TestDunders:
    """魔法方法。"""

    def test_str(self) -> None:
        sb = StringBuilder("hello")
        assert str(sb) == "hello"

    def test_eq_with_str(self) -> None:
        sb = StringBuilder("hello")
        assert sb == "hello"

    def test_eq_with_string_builder(self) -> None:
        sb1 = StringBuilder("hello")
        sb2 = StringBuilder("hello")
        sb3 = StringBuilder("world")
        assert sb1 == sb2
        assert sb1 != sb3

    def test_eq_other_type(self) -> None:
        sb = StringBuilder("123")
        assert (sb == 123) is False

    def test_repr(self) -> None:
        sb = StringBuilder("hi")
        assert repr(sb) == "StringBuilder('hi')"

    def test_iter(self) -> None:
        sb = StringBuilder("abc")
        assert list(sb) == ["a", "b", "c"]


class TestChaining:
    """链式调用端到端。"""

    def test_chain(self) -> None:
        sb = StringBuilder("Hello").append(", ").append("World").append_line("!").insert(5, "X")
        assert sb.to_string() == "HelloX, World!\n"
