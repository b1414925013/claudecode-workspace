"""IoUtil 单元测试。"""

from __future__ import annotations

import io

import pytest

from pyhutool.core.exceptions import UtilError
from pyhutool.io import AsyncIoUtil, IoUtil


class TestCopy:
    """同步拷贝。"""

    def test_copy_bytes(self) -> None:
        src = io.BytesIO(b"hello world")
        dst = io.BytesIO()
        n = IoUtil.copy(src, dst)
        assert n == 11
        assert dst.getvalue() == b"hello world"

    def test_copy_empty(self) -> None:
        src = io.BytesIO(b"")
        dst = io.BytesIO()
        assert IoUtil.copy(src, dst) == 0
        assert dst.getvalue() == b""

    def test_copy_large(self) -> None:
        payload = b"x" * 20000
        src = io.BytesIO(payload)
        dst = io.BytesIO()
        n = IoUtil.copy(src, dst, buffer_size=4096)
        assert n == 20000
        assert dst.getvalue() == payload

    def test_copy_invalid_buffer_size(self) -> None:
        src = io.BytesIO(b"a")
        dst = io.BytesIO()
        with pytest.raises(ValueError):
            IoUtil.copy(src, dst, buffer_size=0)

    def test_copy_reader(self) -> None:
        src = io.StringIO("line1\nline2\n")
        dst = io.StringIO()
        n = IoUtil.copy_reader(src, dst)
        assert n == 12
        assert dst.getvalue() == "line1\nline2\n"


class TestRead:
    """同步读取。"""

    def test_read_bytes(self) -> None:
        assert IoUtil.read_bytes(io.BytesIO(b"abc")) == b"abc"

    def test_read_utf8(self) -> None:
        assert IoUtil.read_utf8(io.BytesIO("你好".encode())) == "你好"

    def test_read_str(self) -> None:
        assert IoUtil.read_str(io.StringIO("hello")) == "hello"

    def test_read_lines(self) -> None:
        result = IoUtil.read_lines(io.StringIO("a\nb\r\nc\n"))
        assert result == ["a", "b", "c"]


class TestWrite:
    """同步写入。"""

    def test_write_bytes(self) -> None:
        dst = io.BytesIO()
        n = IoUtil.write(dst, b"abc")
        assert n == 3
        assert dst.getvalue() == b"abc"

    def test_write_str_default_utf8(self) -> None:
        dst = io.BytesIO()
        n = IoUtil.write(dst, "你好")
        assert n == 6
        assert dst.getvalue() == "你好".encode()

    def test_write_str_other_charset(self) -> None:
        dst = io.BytesIO()
        IoUtil.write(dst, "abc", charset="ascii")
        assert dst.getvalue() == b"abc"

    def test_write_lines(self) -> None:
        dst = io.StringIO()
        n = IoUtil.write_lines(dst, ["a", "b", "c"])
        assert n == 3
        assert dst.getvalue() == "a\nb\nc\n"


class TestCloseFlush:
    """flush / close。"""

    def test_flush_none(self) -> None:
        # 不应抛错
        IoUtil.flush(None)

    def test_flush_callable(self) -> None:
        called: list[bool] = []

        class FakeStream:
            def flush(self) -> None:
                called.append(True)

        IoUtil.flush(FakeStream())  # type: ignore[arg-type]
        assert called == [True]

    def test_close_none(self) -> None:
        IoUtil.close(None)

    def test_close_quietly(self) -> None:
        class BadClose:
            def close(self) -> None:
                raise OSError("boom")

        # 异常被吞掉
        IoUtil.close(BadClose())  # type: ignore[arg-type]


class TestObj:
    """对象序列化。"""

    def test_write_read_obj_roundtrip(self) -> None:
        buf = io.BytesIO()
        IoUtil.write_obj(buf, {"a": 1, "b": [2, 3]})
        buf.seek(0)
        result = IoUtil.read_obj(buf)
        assert result == {"a": 1, "b": [2, 3]}

    def test_read_obj_invalid(self) -> None:
        buf = io.BytesIO(b"not a pickle")
        with pytest.raises(UtilError):
            IoUtil.read_obj(buf)


class TestAsyncIoUtil:
    """AsyncIoUtil 异步覆盖。"""

    @pytest.mark.asyncio
    async def test_copy_bytes(self) -> None:
        src = io.BytesIO(b"hello")
        dst = io.BytesIO()
        n = await AsyncIoUtil.copy(src, dst)
        assert n == 5
        assert dst.getvalue() == b"hello"

    @pytest.mark.asyncio
    async def test_read_utf8(self) -> None:
        result = await AsyncIoUtil.read_utf8(io.BytesIO("你好".encode()))
        assert result == "你好"

    @pytest.mark.asyncio
    async def test_read_lines(self) -> None:
        result = await AsyncIoUtil.read_lines(io.StringIO("a\nb\n"))
        assert result == ["a", "b"]

    @pytest.mark.asyncio
    async def test_write_bytes(self) -> None:
        dst = io.BytesIO()
        n = await AsyncIoUtil.write(dst, b"abc")
        assert n == 3
        assert dst.getvalue() == b"abc"

    @pytest.mark.asyncio
    async def test_write_lines_sync_iterable(self) -> None:
        dst = io.StringIO()
        n = await AsyncIoUtil.write_lines(dst, ["a", "b"])
        assert n == 2
        assert dst.getvalue() == "a\nb\n"

    @pytest.mark.asyncio
    async def test_write_lines_async_iterable(self) -> None:
        from collections.abc import AsyncIterator

        async def agen() -> AsyncIterator[str]:
            yield "x"
            yield "y"

        dst = io.StringIO()
        n = await AsyncIoUtil.write_lines(dst, agen())
        assert n == 2
        assert dst.getvalue() == "x\ny\n"

    @pytest.mark.asyncio
    async def test_close(self) -> None:
        # 不抛错即可
        await AsyncIoUtil.close(None)

    @pytest.mark.asyncio
    async def test_obj_roundtrip(self) -> None:
        buf = io.BytesIO()
        await AsyncIoUtil.write_obj(buf, {"x": 1})
        buf.seek(0)
        result = await AsyncIoUtil.read_obj(buf)
        assert result == {"x": 1}
