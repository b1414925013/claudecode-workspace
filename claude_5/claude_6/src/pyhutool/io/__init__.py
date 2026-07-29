"""pyhutool.io - 文件与流工具模块（零依赖，sync + async 双套 API）。

对齐 Hutool 的 ``cn.hutool.core.io`` 包，提供：

- ``IoUtil``        字节流/字符流读写、拷贝、关闭
- ``FileUtil``      文件/目录读写、复制、移动、列举（含 ``async`` 版本）
- ``ResourceUtil``  classpath 资源加载

异步实现说明
------------
本模块为保持核心零依赖，``async`` 版本通过 ``asyncio.to_thread`` 把阻塞
I/O 委托到线程池执行，足以应对大多数文件场景；如需更高吞吐，可后续提供
基于 ``aiofiles`` 的扩展实现（``pyhutool.io.aio`` extras）。
"""

from pyhutool.io.file_util import AsyncFileUtil, FileUtil
from pyhutool.io.io_util import AsyncIoUtil, IoUtil
from pyhutool.io.resource_util import ResourceUtil

__all__ = [
    "AsyncFileUtil",
    "AsyncIoUtil",
    "FileUtil",
    "IoUtil",
    "ResourceUtil",
]
