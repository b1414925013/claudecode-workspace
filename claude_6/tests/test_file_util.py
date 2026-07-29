"""FileUtil 单元测试。"""

from __future__ import annotations

from pathlib import Path

import pytest

from pyhutool.core.exceptions import UtilError
from pyhutool.io import AsyncFileUtil, FileUtil


class TestBasic:
    """基础信息。"""

    def test_exists(self, tmp_path: Path) -> None:
        f = tmp_path / "a.txt"
        f.write_text("hi", encoding="utf-8")
        assert FileUtil.exists(f) is True
        assert FileUtil.exists(tmp_path / "missing") is False

    def test_is_file_and_dir(self, tmp_path: Path) -> None:
        f = tmp_path / "a.txt"
        f.write_text("hi", encoding="utf-8")
        assert FileUtil.is_file(f) is True
        assert FileUtil.is_directory(f) is False
        assert FileUtil.is_directory(tmp_path) is True
        assert FileUtil.is_file(tmp_path) is False

    def test_size(self, tmp_path: Path) -> None:
        f = tmp_path / "a.txt"
        f.write_bytes(b"hello")
        assert FileUtil.size(f) == 5

    def test_size_missing_raises(self, tmp_path: Path) -> None:
        with pytest.raises(UtilError):
            FileUtil.size(tmp_path / "missing")

    def test_get_temp_dir(self) -> None:
        p = FileUtil.get_temp_dir()
        assert p.exists() and p.is_dir()

    def test_get_user_home(self) -> None:
        p = FileUtil.get_user_home()
        assert p.exists() and p.is_dir()


class TestRead:
    """读取。"""

    def test_read_utf8(self, tmp_path: Path) -> None:
        f = tmp_path / "a.txt"
        f.write_text("你好", encoding="utf-8")
        assert FileUtil.read_utf8(f) == "你好"

    def test_read_string(self, tmp_path: Path) -> None:
        f = tmp_path / "a.txt"
        f.write_text("hello", encoding="ascii")
        assert FileUtil.read_string(f, charset="ascii") == "hello"

    def test_read_bytes(self, tmp_path: Path) -> None:
        f = tmp_path / "a.bin"
        f.write_bytes(b"\x00\x01\x02")
        assert FileUtil.read_bytes(f) == b"\x00\x01\x02"

    def test_read_lines(self, tmp_path: Path) -> None:
        f = tmp_path / "a.txt"
        # 用 write_bytes 写入精确字节，避免 Windows 平台 write_text 把 \n
        # 翻译成 \r\n 造成 \r\n -> \r\r\n 的二次翻译
        f.write_bytes(b"a\nb\r\nc\n")
        assert FileUtil.read_lines(f) == ["a", "b", "c"]


class TestWrite:
    """写入。"""

    def test_write_utf8_overwrite(self, tmp_path: Path) -> None:
        f = tmp_path / "a.txt"
        FileUtil.write_utf8("hello", f)
        assert f.read_text(encoding="utf-8") == "hello"
        FileUtil.write_utf8("world", f)
        assert f.read_text(encoding="utf-8") == "world"

    def test_write_utf8_append(self, tmp_path: Path) -> None:
        f = tmp_path / "a.txt"
        FileUtil.write_utf8("a", f)
        FileUtil.append_utf8("b", f)
        assert f.read_text(encoding="utf-8") == "ab"

    def test_write_bytes(self, tmp_path: Path) -> None:
        f = tmp_path / "a.bin"
        FileUtil.write_bytes(b"\xff\xfe", f)
        assert f.read_bytes() == b"\xff\xfe"

    def test_write_lines(self, tmp_path: Path) -> None:
        f = tmp_path / "a.txt"
        n = FileUtil.write_lines(["a", "b", "c"], f)
        assert n == 3
        assert f.read_text(encoding="utf-8") == "a\nb\nc\n"

    def test_write_creates_parent_dirs(self, tmp_path: Path) -> None:
        f = tmp_path / "sub" / "dir" / "a.txt"
        FileUtil.write_utf8("hi", f)
        assert f.read_text(encoding="utf-8") == "hi"


class TestCreateDelete:
    """创建 / 删除。"""

    def test_touch_creates_file(self, tmp_path: Path) -> None:
        f = tmp_path / "a.txt"
        assert not f.exists()
        FileUtil.touch(f)
        assert f.exists() and f.is_file()

    def test_touch_creates_parent(self, tmp_path: Path) -> None:
        f = tmp_path / "sub" / "a.txt"
        FileUtil.touch(f)
        assert f.exists()

    def test_mkdir(self, tmp_path: Path) -> None:
        d = tmp_path / "a" / "b"
        FileUtil.mkdir(d)
        assert d.is_dir()
        # 幂等
        FileUtil.mkdir(d)
        assert d.is_dir()

    def test_del_file(self, tmp_path: Path) -> None:
        f = tmp_path / "a.txt"
        f.write_text("hi", encoding="utf-8")
        assert FileUtil.del_(f) is True
        assert not f.exists()
        # 再删返回 False
        assert FileUtil.del_(f) is False

    def test_del_directory(self, tmp_path: Path) -> None:
        d = tmp_path / "a"
        (d / "sub").mkdir(parents=True)
        (d / "a.txt").write_text("hi", encoding="utf-8")
        assert FileUtil.del_(d) is True
        assert not d.exists()

    def test_clean(self, tmp_path: Path) -> None:
        d = tmp_path / "a"
        d.mkdir()
        (d / "a.txt").write_text("hi", encoding="utf-8")
        (d / "sub").mkdir()
        n = FileUtil.clean(d)
        assert n == 2
        assert d.exists() and d.is_dir() and list(d.iterdir()) == []

    def test_clean_missing(self, tmp_path: Path) -> None:
        assert FileUtil.clean(tmp_path / "missing") == 0


class TestCopyMove:
    """复制 / 移动。"""

    def test_copy_file(self, tmp_path: Path) -> None:
        src = tmp_path / "a.txt"
        src.write_text("hi", encoding="utf-8")
        dst = tmp_path / "b.txt"
        FileUtil.copy(src, dst)
        assert dst.read_text(encoding="utf-8") == "hi"
        # 源仍存在
        assert src.exists()

    def test_copy_to_dir(self, tmp_path: Path) -> None:
        src = tmp_path / "a.txt"
        src.write_text("hi", encoding="utf-8")
        dst_dir = tmp_path / "out"
        dst_dir.mkdir()
        result = FileUtil.copy(src, dst_dir)
        assert result == dst_dir / "a.txt"
        assert result.read_text(encoding="utf-8") == "hi"

    def test_copy_directory(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        (src / "sub").mkdir(parents=True)
        (src / "a.txt").write_text("hi", encoding="utf-8")
        (src / "sub" / "b.txt").write_text("yo", encoding="utf-8")
        dst = tmp_path / "dst"
        FileUtil.copy(src, dst)
        assert (dst / "a.txt").read_text(encoding="utf-8") == "hi"
        assert (dst / "sub" / "b.txt").read_text(encoding="utf-8") == "yo"

    def test_copy_no_replace_raises(self, tmp_path: Path) -> None:
        src = tmp_path / "a.txt"
        src.write_text("hi", encoding="utf-8")
        dst = tmp_path / "b.txt"
        dst.write_text("old", encoding="utf-8")
        with pytest.raises(UtilError):
            FileUtil.copy(src, dst, replace_existing=False)

    def test_copy_missing_raises(self, tmp_path: Path) -> None:
        with pytest.raises(UtilError):
            FileUtil.copy(tmp_path / "missing", tmp_path / "out")

    def test_move_file(self, tmp_path: Path) -> None:
        src = tmp_path / "a.txt"
        src.write_text("hi", encoding="utf-8")
        dst = tmp_path / "b.txt"
        FileUtil.move(src, dst)
        assert dst.read_text(encoding="utf-8") == "hi"
        assert not src.exists()

    def test_rename(self, tmp_path: Path) -> None:
        src = tmp_path / "a.txt"
        src.write_text("hi", encoding="utf-8")
        new = FileUtil.rename(src, "b.txt")
        assert new == tmp_path / "b.txt"
        assert new.read_text(encoding="utf-8") == "hi"
        assert not src.exists()


class TestList:
    """列举。"""

    def test_list_files_flat(self, tmp_path: Path) -> None:
        (tmp_path / "a.txt").write_text("a", encoding="utf-8")
        (tmp_path / "b.txt").write_text("b", encoding="utf-8")
        (tmp_path / "sub").mkdir()
        (tmp_path / "sub" / "c.txt").write_text("c", encoding="utf-8")
        files = FileUtil.list_files(tmp_path)
        names = sorted(p.name for p in files)
        assert names == ["a.txt", "b.txt"]

    def test_list_files_recursive(self, tmp_path: Path) -> None:
        (tmp_path / "a.txt").write_text("a", encoding="utf-8")
        (tmp_path / "sub").mkdir()
        (tmp_path / "sub" / "c.txt").write_text("c", encoding="utf-8")
        files = FileUtil.list_files(tmp_path, recursive=True)
        names = sorted(p.name for p in files)
        assert names == ["a.txt", "c.txt"]

    def test_list_dirs(self, tmp_path: Path) -> None:
        (tmp_path / "a").mkdir()
        (tmp_path / "b").mkdir()
        (tmp_path / "a.txt").write_text("a", encoding="utf-8")
        dirs = FileUtil.list_dirs(tmp_path)
        names = sorted(p.name for p in dirs)
        assert names == ["a", "b"]

    def test_list_files_missing(self, tmp_path: Path) -> None:
        assert FileUtil.list_files(tmp_path / "missing") == []


class TestAsyncFileUtil:
    """AsyncFileUtil 异步覆盖。"""

    @pytest.mark.asyncio
    async def test_read_write_utf8(self, tmp_path: Path) -> None:
        f = tmp_path / "a.txt"
        await AsyncFileUtil.write_utf8("hello", f)
        assert await AsyncFileUtil.read_utf8(f) == "hello"

    @pytest.mark.asyncio
    async def test_read_bytes(self, tmp_path: Path) -> None:
        f = tmp_path / "a.bin"
        await AsyncFileUtil.write_bytes(b"\x00\x01", f)
        assert await AsyncFileUtil.read_bytes(f) == b"\x00\x01"

    @pytest.mark.asyncio
    async def test_read_lines(self, tmp_path: Path) -> None:
        f = tmp_path / "a.txt"
        await AsyncFileUtil.write_lines(["a", "b"], f)
        assert await AsyncFileUtil.read_lines(f) == ["a", "b"]

    @pytest.mark.asyncio
    async def test_touch_mkdir(self, tmp_path: Path) -> None:
        f = tmp_path / "sub" / "a.txt"
        await AsyncFileUtil.touch(f)
        assert await AsyncFileUtil.is_file(f) is True
        assert await AsyncFileUtil.exists(f) is True

    @pytest.mark.asyncio
    async def test_del(self, tmp_path: Path) -> None:
        f = tmp_path / "a.txt"
        f.write_text("hi", encoding="utf-8")
        assert await AsyncFileUtil.del_(f) is True
        assert await AsyncFileUtil.exists(f) is False

    @pytest.mark.asyncio
    async def test_copy(self, tmp_path: Path) -> None:
        src = tmp_path / "a.txt"
        src.write_text("hi", encoding="utf-8")
        dst = tmp_path / "b.txt"
        await AsyncFileUtil.copy(src, dst)
        assert dst.read_text(encoding="utf-8") == "hi"

    @pytest.mark.asyncio
    async def test_move(self, tmp_path: Path) -> None:
        src = tmp_path / "a.txt"
        src.write_text("hi", encoding="utf-8")
        dst = tmp_path / "b.txt"
        await AsyncFileUtil.move(src, dst)
        assert dst.read_text(encoding="utf-8") == "hi"
        assert not src.exists()

    @pytest.mark.asyncio
    async def test_list_files(self, tmp_path: Path) -> None:
        (tmp_path / "a.txt").write_text("a", encoding="utf-8")
        files = await AsyncFileUtil.list_files(tmp_path)
        assert len(files) == 1

    @pytest.mark.asyncio
    async def test_size(self, tmp_path: Path) -> None:
        f = tmp_path / "a.txt"
        f.write_bytes(b"hello")
        assert await AsyncFileUtil.size(f) == 5
