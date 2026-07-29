"""classpath 资源加载工具。

对齐 Hutool 的 ``cn.hutool.core.io.resource.ResourceUtil``，从 Python
``importlib.resources`` 中按 "classpath" 语义加载资源。

约定
----
Hutool 把 ``classpath:`` 视为类路径根。pyhutool 用包名 + 资源相对路径来
定位，例如 ``ResourceUtil.read_string("pyhutool.core", "messages/zh.txt")``
等价于 Hutool ``ResourceUtil.readUtf8Str("messages/zh.txt")``（假设资源
位于 ``pyhutool.core`` 包下）。

为了避免歧义，本工具显式要求传入 ``package`` 作为锚点包，让 ``importlib``
的标准机制负责解析，行为可移植且不依赖 ``__file__``。
"""

from __future__ import annotations

from importlib import resources
from typing import Final

from pyhutool.core.exceptions import UtilError

__all__ = ["ResourceUtil"]

_UTF8: Final[str] = "UTF-8"


class ResourceUtil:
    """资源加载工具类。"""

    @staticmethod
    def get_resource_url(package: str, resource: str) -> str:
        """获取资源的 URL 字符串。

        Parameters
        ----------
        package:
            锚点包名（如 ``pyhutool.core``）。
        resource:
            相对该包的资源路径（使用 ``/`` 分隔）。
        """
        try:
            # Python 3.11+：直接使用 Traversable.as_file + resolve
            anchor = resources.files(package) / resource
        except (ModuleNotFoundError, FileNotFoundError) as e:
            raise UtilError(f"资源不存在: {package}/{resource}", cause=e) from e
        try:
            # 命名空间包或 ZIP 内资源 → 返回 traver 资源 URI
            with resources.as_file(anchor) as path:
                return path.resolve().as_uri()
        except (FileNotFoundError, OSError) as e:
            raise UtilError(f"资源无法解析为 URL: {package}/{resource}", cause=e) from e

    @staticmethod
    def read_string(package: str, resource: str, charset: str = _UTF8) -> str:
        """读取 classpath 资源为字符串。

        对应 Hutool ``ResourceUtil.readUtf8Str``。
        """
        try:
            return (resources.files(package) / resource).read_text(encoding=charset)
        except (ModuleNotFoundError, FileNotFoundError, UnicodeDecodeError) as e:
            raise UtilError(f"读取资源失败: {package}/{resource}", cause=e) from e

    @staticmethod
    def read_bytes(package: str, resource: str) -> bytes:
        """读取 classpath 资源为字节。"""
        try:
            return (resources.files(package) / resource).read_bytes()
        except (ModuleNotFoundError, FileNotFoundError) as e:
            raise UtilError(f"读取资源失败: {package}/{resource}", cause=e) from e

    @staticmethod
    def exists(package: str, resource: str) -> bool:
        """判断 classpath 资源是否存在。"""
        try:
            anchor = resources.files(package) / resource
        except (ModuleNotFoundError, FileNotFoundError):
            return False
        try:
            return anchor.is_file()
        except OSError:
            return False
