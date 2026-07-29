"""流工具。

对齐 Hutool 的 ``cn.hutool.core.io.IoUtil``，提供字节/字符流的读写、
拷贝、关闭等高频操作。所有 ``close`` 操作均使用 ``contextlib.suppress``
吞掉 ``OSError``，与 Hutool ``closeQuietly`` 一致。

同步版（``IoUtil``）与异步版（``AsyncIoUtil``）一一对应。异步版通过
``asyncio.to_thread`` 把阻塞 I/O 委托到默认线程池。
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterable, Iterable
from contextlib import suppress
from typing import IO, AnyStr, Final

from pyhutool.core.exceptions import UtilError

__all__ = ["AsyncIoUtil", "IoUtil"]

# 默认缓冲区大小（8 KiB，与 Hutool ``DEFAULT_BUFFER_SIZE`` 一致）
_DEFAULT_BUFFER_SIZE: Final[int] = 8192
# UTF-8 默认字符集名
_UTF8: Final[str] = "UTF-8"


class IoUtil:
    """同步流工具类，全部为静态方法。"""

    # ------------------------------------------------------------------
    # 拷贝
    # ------------------------------------------------------------------
    @staticmethod
    def copy(
        input_stream: IO[bytes],
        output_stream: IO[bytes],
        buffer_size: int = _DEFAULT_BUFFER_SIZE,
    ) -> int:
        """拷贝字节流，返回拷贝的字节数。

        对应 Hutool ``IoUtil.copy(InputStream, OutputStream)``。

        Parameters
        ----------
        input_stream:
            输入字节流。
        output_stream:
            输出字节流。
        buffer_size:
            缓冲区大小，默认 8 KiB。
        """
        if buffer_size <= 0:
            raise ValueError("buffer_size 必须大于 0")
        total = 0
        while True:
            chunk = input_stream.read(buffer_size)
            if not chunk:
                break
            output_stream.write(chunk)
            total += len(chunk)
        return total

    @staticmethod
    def copy_reader(
        reader: IO[str],
        writer: IO[str],
        buffer_size: int = _DEFAULT_BUFFER_SIZE,
    ) -> int:
        """拷贝字符流，返回拷贝的字符数。"""
        if buffer_size <= 0:
            raise ValueError("buffer_size 必须大于 0")
        total = 0
        while True:
            chunk = reader.read(buffer_size)
            if not chunk:
                break
            writer.write(chunk)
            total += len(chunk)
        return total

    # ------------------------------------------------------------------
    # 读取
    # ------------------------------------------------------------------
    @staticmethod
    def read_bytes(input_stream: IO[bytes]) -> bytes:
        """读取全部字节。"""
        return input_stream.read()

    @staticmethod
    def read_utf8(input_stream: IO[bytes]) -> str:
        """以 UTF-8 读取字节流为字符串。"""
        return input_stream.read().decode(_UTF8)

    @staticmethod
    def read_str(reader: IO[str]) -> str:
        """读取字符流为字符串。"""
        return reader.read()

    @staticmethod
    def read_lines(reader: IO[str]) -> list[str]:
        """按行读取字符流，返回各行（去除行尾换行符）。"""
        return [line.rstrip("\r\n") for line in reader]

    # ------------------------------------------------------------------
    # 写入
    # ------------------------------------------------------------------
    @staticmethod
    def write(
        output_stream: IO[bytes],
        data: bytes | str,
        charset: str = _UTF8,
    ) -> int:
        """向字节流写入数据。

        Parameters
        ----------
        output_stream:
            目标字节流。
        data:
            数据；``str`` 按 ``charset`` 编码。
        charset:
            字符集，默认 UTF-8。
        """
        payload = data.encode(charset) if isinstance(data, str) else data
        output_stream.write(payload)
        return len(payload)

    @staticmethod
    def write_lines(output_stream: IO[str], lines: Iterable[str]) -> int:
        """逐行写入字符流，自动追加 ``\\n``。返回写入行数。"""
        count = 0
        for line in lines:
            output_stream.write(line + "\n")
            count += 1
        return count

    # ------------------------------------------------------------------
    # 刷新 / 关闭
    # ------------------------------------------------------------------
    @staticmethod
    def flush(stream: IO[AnyStr]) -> None:
        """刷新流。``None`` 静默跳过。"""
        if stream is None:
            return
        flushable = getattr(stream, "flush", None)
        if callable(flushable):
            flushable()

    @staticmethod
    def close(closeable: object | None) -> None:
        """静默关闭 ``Closeable``/``AutoCloseable`` 对象。

        对应 Hutool ``IoUtil.close``，任何异常被吞掉。
        """
        if closeable is None:
            return
        close_method = getattr(closeable, "close", None)
        if callable(close_method):
            with suppress(OSError):
                close_method()

    # ------------------------------------------------------------------
    # 对象序列化（对齐 readObj / writeObj）
    # ------------------------------------------------------------------
    @staticmethod
    def read_obj(input_stream: IO[bytes]) -> object:
        """使用 ``pickle`` 反序列化对象。

        对应 Hutool ``IoUtil.readObj``。注意：Python ``pickle`` 反序列化
        等价于执行任意代码，仅对受信任数据使用。
        """
        import pickle

        try:
            return pickle.load(input_stream)
        except (pickle.PickleError, EOFError, AttributeError) as e:
            raise UtilError("反序列化对象失败", cause=e) from e

    @staticmethod
    def write_obj(output_stream: IO[bytes], obj: object) -> None:
        """使用 ``pickle`` 序列化对象到流。"""
        import pickle

        try:
            pickle.dump(obj, output_stream)
        except (pickle.PickleError, TypeError) as e:
            raise UtilError("序列化对象失败", cause=e) from e


class AsyncIoUtil:
    """异步流工具类。

    每个方法对应 ``IoUtil`` 中的同名方法，通过 ``asyncio.to_thread``
    在线程池中执行阻塞 I/O。所有协程均 ``await`` 友好。
    """

    @staticmethod
    async def copy(
        input_stream: IO[bytes],
        output_stream: IO[bytes],
        buffer_size: int = _DEFAULT_BUFFER_SIZE,
    ) -> int:
        """异步拷贝字节流。"""
        return await asyncio.to_thread(IoUtil.copy, input_stream, output_stream, buffer_size)

    @staticmethod
    async def copy_reader(
        reader: IO[str],
        writer: IO[str],
        buffer_size: int = _DEFAULT_BUFFER_SIZE,
    ) -> int:
        """异步拷贝字符流。"""
        return await asyncio.to_thread(IoUtil.copy_reader, reader, writer, buffer_size)

    @staticmethod
    async def read_bytes(input_stream: IO[bytes]) -> bytes:
        """异步读取全部字节。"""
        return await asyncio.to_thread(IoUtil.read_bytes, input_stream)

    @staticmethod
    async def read_utf8(input_stream: IO[bytes]) -> str:
        """异步以 UTF-8 读取字节流为字符串。"""
        return await asyncio.to_thread(IoUtil.read_utf8, input_stream)

    @staticmethod
    async def read_str(reader: IO[str]) -> str:
        """异步读取字符流为字符串。"""
        return await asyncio.to_thread(IoUtil.read_str, reader)

    @staticmethod
    async def read_lines(reader: IO[str]) -> list[str]:
        """异步按行读取字符流。"""
        return await asyncio.to_thread(IoUtil.read_lines, reader)

    @staticmethod
    async def write(
        output_stream: IO[bytes],
        data: bytes | str,
        charset: str = _UTF8,
    ) -> int:
        """异步向字节流写入数据。"""
        return await asyncio.to_thread(IoUtil.write, output_stream, data, charset)

    @staticmethod
    async def write_lines(output_stream: IO[str], lines: AsyncIterable[str] | Iterable[str]) -> int:
        """异步逐行写入字符流。

        若 ``lines`` 是 ``AsyncIterable``，会按需 ``await``；否则直接迭代。
        """
        if isinstance(lines, AsyncIterable):
            count = 0
            async for line in lines:
                await asyncio.to_thread(output_stream.write, line + "\n")
                count += 1
            return count
        return await asyncio.to_thread(IoUtil.write_lines, output_stream, lines)

    @staticmethod
    async def flush(stream: IO[AnyStr]) -> None:
        """异步刷新流。"""
        await asyncio.to_thread(IoUtil.flush, stream)

    @staticmethod
    async def close(closeable: object | None) -> None:
        """异步静默关闭流。"""
        await asyncio.to_thread(IoUtil.close, closeable)

    @staticmethod
    async def read_obj(input_stream: IO[bytes]) -> object:
        """异步反序列化对象。"""
        return await asyncio.to_thread(IoUtil.read_obj, input_stream)

    @staticmethod
    async def write_obj(output_stream: IO[bytes], obj: object) -> None:
        """异步序列化对象到流。"""
        await asyncio.to_thread(IoUtil.write_obj, output_stream, obj)
