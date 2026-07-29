"""文件工具。

对齐 Hutool 的 ``cn.hutool.core.io.FileUtil``，提供文件/目录的读写、
创建、复制、移动、删除、列举等高频操作。底层基于 ``pathlib`` 与
``shutil`` 实现，所有路径均接受 ``str | os.PathLike | pathlib.Path``。

同步版（``FileUtil``）与异步版（``AsyncFileUtil``）一一对应，异步版
通过 ``asyncio.to_thread`` 在线程池中执行阻塞 I/O。
"""

from __future__ import annotations

import asyncio
import os
import shutil
from collections.abc import Iterable
from pathlib import Path
from typing import Final

from pyhutool.core.exceptions import UtilError

__all__ = ["AsyncFileUtil", "FileUtil"]

_UTF8: Final[str] = "UTF-8"


def _to_path(path: str | os.PathLike[str] | Path) -> Path:
    """把任意路径对象规范化为 ``pathlib.Path``。"""
    return Path(path)


class FileUtil:
    """同步文件工具类，全部为静态方法。"""

    # ------------------------------------------------------------------
    # 基础信息
    # ------------------------------------------------------------------
    @staticmethod
    def exists(path: str | os.PathLike[str] | Path) -> bool:
        """判断路径是否存在。"""
        return _to_path(path).exists()

    @staticmethod
    def is_file(path: str | os.PathLike[str] | Path) -> bool:
        """判断是否为文件。"""
        return _to_path(path).is_file()

    @staticmethod
    def is_directory(path: str | os.PathLike[str] | Path) -> bool:
        """判断是否为目录。"""
        return _to_path(path).is_dir()

    @staticmethod
    def size(path: str | os.PathLike[str] | Path) -> int:
        """返回文件大小（字节）。不存在时抛 ``UtilError``。"""
        p = _to_path(path)
        if not p.exists():
            raise UtilError(f"文件不存在: {p}")
        return p.stat().st_size

    @staticmethod
    def get_temp_dir() -> Path:
        """返回系统临时目录。对应 Hutool ``FileUtil.getTmpDirPath``。"""
        return Path(_tempdir_first())

    @staticmethod
    def get_user_home() -> Path:
        """返回当前用户主目录。"""
        return Path(os.path.expanduser("~"))

    # ------------------------------------------------------------------
    # 读
    # ------------------------------------------------------------------
    @staticmethod
    def read_utf8(path: str | os.PathLike[str] | Path) -> str:
        """以 UTF-8 读取文件内容为字符串。"""
        return _to_path(path).read_text(encoding=_UTF8)

    @staticmethod
    def read_string(path: str | os.PathLike[str] | Path, charset: str = _UTF8) -> str:
        """以指定字符集读取文件。"""
        return _to_path(path).read_text(encoding=charset)

    @staticmethod
    def read_bytes(path: str | os.PathLike[str] | Path) -> bytes:
        """读取文件全部字节。"""
        return _to_path(path).read_bytes()

    @staticmethod
    def read_lines(
        path: str | os.PathLike[str] | Path,
        charset: str = _UTF8,
    ) -> list[str]:
        """按行读取，返回去除行尾换行符的列表。"""
        return _to_path(path).read_text(encoding=charset).splitlines()

    # ------------------------------------------------------------------
    # 写
    # ------------------------------------------------------------------
    @staticmethod
    def write_utf8(
        content: str,
        path: str | os.PathLike[str] | Path,
        append: bool = False,
    ) -> int:
        """以 UTF-8 写字符串到文件。

        ``append=True`` 时追加；否则覆盖。返回写入字符数。
        """
        p = _to_path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if append else "w"
        with p.open(mode, encoding=_UTF8) as f:
            f.write(content)
            return len(content)

    @staticmethod
    def write_bytes(
        content: bytes,
        path: str | os.PathLike[str] | Path,
        append: bool = False,
    ) -> int:
        """写字节到文件，返回写入字节数。"""
        p = _to_path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        mode = "ab" if append else "wb"
        with p.open(mode) as f:
            f.write(content)
            return len(content)

    @staticmethod
    def write_lines(
        lines: Iterable[str],
        path: str | os.PathLike[str] | Path,
        charset: str = _UTF8,
        append: bool = False,
    ) -> int:
        """逐行写入，每行末尾追加 ``\\n``。返回行数。"""
        p = _to_path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if append else "w"
        count = 0
        with p.open(mode, encoding=charset) as f:
            for line in lines:
                f.write(line + "\n")
                count += 1
        return count

    @staticmethod
    def append_utf8(
        content: str,
        path: str | os.PathLike[str] | Path,
    ) -> int:
        """追加 UTF-8 字符串到文件末尾。"""
        return FileUtil.write_utf8(content, path, append=True)

    # ------------------------------------------------------------------
    # 创建 / 删除
    # ------------------------------------------------------------------
    @staticmethod
    def touch(path: str | os.PathLike[str] | Path) -> Path:
        """创建空文件（含父目录）。已存在则更新修改时间。

        对应 Hutool ``FileUtil.touch``。
        """
        p = _to_path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists():
            p.touch()
        else:
            # 更新修改时间
            os.utime(p, None)
        return p

    @staticmethod
    def mkdir(path: str | os.PathLike[str] | Path) -> Path:
        """创建目录（含父目录）。已存在则静默返回。"""
        p = _to_path(path)
        p.mkdir(parents=True, exist_ok=True)
        return p

    @staticmethod
    def del_(path: str | os.PathLike[str] | Path) -> bool:
        """删除文件或目录（递归）。

        对应 Hutool ``FileUtil.del``。``不存在时返回 ``False``。
        """
        p = _to_path(path)
        if not p.exists():
            return False
        try:
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()
        except OSError as e:
            raise UtilError(f"删除失败: {p}", cause=e) from e
        return True

    @staticmethod
    def clean(path: str | os.PathLike[str] | Path) -> int:
        """清空目录内容（保留目录本身）。返回删除项数。"""
        p = _to_path(path)
        if not p.exists() or not p.is_dir():
            return 0
        count = 0
        for child in p.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
            count += 1
        return count

    # ------------------------------------------------------------------
    # 复制 / 移动
    # ------------------------------------------------------------------
    @staticmethod
    def copy(
        src: str | os.PathLike[str] | Path,
        target: str | os.PathLike[str] | Path,
        replace_existing: bool = True,
    ) -> Path:
        """复制文件或目录到 ``target``。

        对应 Hutool ``FileUtil.copy``。``target`` 是目录时拷入其下并使用原文件名。
        """
        src_p = _to_path(src)
        target_p = _to_path(target)
        if not src_p.exists():
            raise UtilError(f"源路径不存在: {src_p}")
        # 目标是已存在目录 → 拷入其下
        if target_p.is_dir():
            target_p = target_p / src_p.name
        if target_p.exists() and not replace_existing:
            raise UtilError(f"目标已存在且未指定覆盖: {target_p}")
        target_p.parent.mkdir(parents=True, exist_ok=True)
        try:
            if src_p.is_dir():
                shutil.copytree(src_p, target_p, dirs_exist_ok=replace_existing)
            else:
                shutil.copy2(src_p, target_p)
        except OSError as e:
            raise UtilError(f"复制失败: {src_p} -> {target_p}", cause=e) from e
        return target_p

    @staticmethod
    def move(
        src: str | os.PathLike[str] | Path,
        target: str | os.PathLike[str] | Path,
        replace_existing: bool = True,
    ) -> Path:
        """移动/重命名文件或目录。"""
        src_p = _to_path(src)
        target_p = _to_path(target)
        if not src_p.exists():
            raise UtilError(f"源路径不存在: {src_p}")
        if target_p.is_dir():
            target_p = target_p / src_p.name
        if target_p.exists() and not replace_existing:
            raise UtilError(f"目标已存在且未指定覆盖: {target_p}")
        target_p.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(src_p, target_p)
        except OSError as e:
            raise UtilError(f"移动失败: {src_p} -> {target_p}", cause=e) from e
        return target_p

    @staticmethod
    def rename(
        src: str | os.PathLike[str] | Path,
        new_name: str,
    ) -> Path:
        """重命名（仅修改文件名，保留父目录）。"""
        src_p = _to_path(src)
        if not src_p.exists():
            raise UtilError(f"源路径不存在: {src_p}")
        target = src_p.with_name(new_name)
        # Path.replace(target) 把 self 重命名为 target；这里要把 src_p → target
        src_p.replace(target)
        return target

    # ------------------------------------------------------------------
    # 列举
    # ------------------------------------------------------------------
    @staticmethod
    def list_files(
        path: str | os.PathLike[str] | Path,
        recursive: bool = False,
    ) -> list[Path]:
        """列出目录下文件（不含子目录本身）。

        Parameters
        ----------
        path:
            目录路径。
        recursive:
            是否递归遍历。
        """
        p = _to_path(path)
        if not p.exists() or not p.is_dir():
            return []
        glob_fn = p.rglob if recursive else p.glob
        return sorted(x for x in glob_fn("*") if x.is_file())

    @staticmethod
    def list_dirs(
        path: str | os.PathLike[str] | Path,
        recursive: bool = False,
    ) -> list[Path]:
        """列出目录下子目录。"""
        p = _to_path(path)
        if not p.exists() or not p.is_dir():
            return []
        glob_fn = p.rglob if recursive else p.glob
        return sorted(x for x in glob_fn("*") if x.is_dir())


class AsyncFileUtil:
    """异步文件工具类。

    每个方法对应 ``FileUtil`` 同名方法，通过 ``asyncio.to_thread`` 在
    线程池中执行阻塞 I/O。
    """

    # ------------------------------------------------------------------
    # 基础信息
    # ------------------------------------------------------------------
    @staticmethod
    async def exists(path: str | os.PathLike[str] | Path) -> bool:
        return await asyncio.to_thread(FileUtil.exists, path)

    @staticmethod
    async def is_file(path: str | os.PathLike[str] | Path) -> bool:
        return await asyncio.to_thread(FileUtil.is_file, path)

    @staticmethod
    async def is_directory(path: str | os.PathLike[str] | Path) -> bool:
        return await asyncio.to_thread(FileUtil.is_directory, path)

    @staticmethod
    async def size(path: str | os.PathLike[str] | Path) -> int:
        return await asyncio.to_thread(FileUtil.size, path)

    @staticmethod
    async def get_temp_dir() -> Path:
        return await asyncio.to_thread(FileUtil.get_temp_dir)

    @staticmethod
    async def get_user_home() -> Path:
        return await asyncio.to_thread(FileUtil.get_user_home)

    # ------------------------------------------------------------------
    # 读
    # ------------------------------------------------------------------
    @staticmethod
    async def read_utf8(path: str | os.PathLike[str] | Path) -> str:
        return await asyncio.to_thread(FileUtil.read_utf8, path)

    @staticmethod
    async def read_string(
        path: str | os.PathLike[str] | Path,
        charset: str = _UTF8,
    ) -> str:
        return await asyncio.to_thread(FileUtil.read_string, path, charset)

    @staticmethod
    async def read_bytes(path: str | os.PathLike[str] | Path) -> bytes:
        return await asyncio.to_thread(FileUtil.read_bytes, path)

    @staticmethod
    async def read_lines(
        path: str | os.PathLike[str] | Path,
        charset: str = _UTF8,
    ) -> list[str]:
        return await asyncio.to_thread(FileUtil.read_lines, path, charset)

    # ------------------------------------------------------------------
    # 写
    # ------------------------------------------------------------------
    @staticmethod
    async def write_utf8(
        content: str,
        path: str | os.PathLike[str] | Path,
        append: bool = False,
    ) -> int:
        return await asyncio.to_thread(FileUtil.write_utf8, content, path, append)

    @staticmethod
    async def write_bytes(
        content: bytes,
        path: str | os.PathLike[str] | Path,
        append: bool = False,
    ) -> int:
        return await asyncio.to_thread(FileUtil.write_bytes, content, path, append)

    @staticmethod
    async def write_lines(
        lines: Iterable[str],
        path: str | os.PathLike[str] | Path,
        charset: str = _UTF8,
        append: bool = False,
    ) -> int:
        return await asyncio.to_thread(FileUtil.write_lines, lines, path, charset, append)

    @staticmethod
    async def append_utf8(
        content: str,
        path: str | os.PathLike[str] | Path,
    ) -> int:
        return await asyncio.to_thread(FileUtil.append_utf8, content, path)

    # ------------------------------------------------------------------
    # 创建 / 删除
    # ------------------------------------------------------------------
    @staticmethod
    async def touch(path: str | os.PathLike[str] | Path) -> Path:
        return await asyncio.to_thread(FileUtil.touch, path)

    @staticmethod
    async def mkdir(path: str | os.PathLike[str] | Path) -> Path:
        return await asyncio.to_thread(FileUtil.mkdir, path)

    @staticmethod
    async def del_(path: str | os.PathLike[str] | Path) -> bool:
        return await asyncio.to_thread(FileUtil.del_, path)

    @staticmethod
    async def clean(path: str | os.PathLike[str] | Path) -> int:
        return await asyncio.to_thread(FileUtil.clean, path)

    # ------------------------------------------------------------------
    # 复制 / 移动
    # ------------------------------------------------------------------
    @staticmethod
    async def copy(
        src: str | os.PathLike[str] | Path,
        target: str | os.PathLike[str] | Path,
        replace_existing: bool = True,
    ) -> Path:
        return await asyncio.to_thread(FileUtil.copy, src, target, replace_existing)

    @staticmethod
    async def move(
        src: str | os.PathLike[str] | Path,
        target: str | os.PathLike[str] | Path,
        replace_existing: bool = True,
    ) -> Path:
        return await asyncio.to_thread(FileUtil.move, src, target, replace_existing)

    @staticmethod
    async def rename(
        src: str | os.PathLike[str] | Path,
        new_name: str,
    ) -> Path:
        return await asyncio.to_thread(FileUtil.rename, src, new_name)

    # ------------------------------------------------------------------
    # 列举
    # ------------------------------------------------------------------
    @staticmethod
    async def list_files(
        path: str | os.PathLike[str] | Path,
        recursive: bool = False,
    ) -> list[Path]:
        return await asyncio.to_thread(FileUtil.list_files, path, recursive)

    @staticmethod
    async def list_dirs(
        path: str | os.PathLike[str] | Path,
        recursive: bool = False,
    ) -> list[Path]:
        return await asyncio.to_thread(FileUtil.list_dirs, path, recursive)


def _tempdir_first() -> str:
    """跨平台获取临时目录，避免 ``tempfile.gettempdir()`` 在某些场景下的缓存问题。"""
    import tempfile

    return tempfile.gettempdir()
