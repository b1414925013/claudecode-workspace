"""ResourceUtil 单元测试。"""

from __future__ import annotations

import pytest

from pyhutool.core.exceptions import UtilError
from pyhutool.io import ResourceUtil

# 注：测试以 ``tests`` 包中的 ``__init__.py`` 作为可读资源


class TestReadResource:
    """读取 classpath 资源。"""

    def test_read_string(self) -> None:
        # tests 包自身存在 __init__.py，读它当作文本资源
        result = ResourceUtil.read_string("tests", "__init__.py")
        assert isinstance(result, str)

    def test_read_bytes(self) -> None:
        result = ResourceUtil.read_bytes("tests", "__init__.py")
        assert isinstance(result, bytes)

    def test_read_missing_package_raises(self) -> None:
        with pytest.raises(UtilError):
            ResourceUtil.read_string("pyhutool.nonexistent_pkg", "x.txt")

    def test_read_missing_resource_raises(self) -> None:
        with pytest.raises(UtilError):
            ResourceUtil.read_string("tests", "no_such_file.txt")


class TestExists:
    """exists 判断。"""

    def test_exists_true(self) -> None:
        assert ResourceUtil.exists("tests", "__init__.py") is True

    def test_exists_false_missing_resource(self) -> None:
        assert ResourceUtil.exists("tests", "no_such_file.txt") is False

    def test_exists_false_missing_package(self) -> None:
        assert ResourceUtil.exists("pyhutool.no_such_pkg", "x.txt") is False


class TestGetResourceUrl:
    """资源 URL 解析。"""

    def test_get_resource_url_for_file(self) -> None:
        url = ResourceUtil.get_resource_url("tests", "__init__.py")
        assert url.startswith("file:")
