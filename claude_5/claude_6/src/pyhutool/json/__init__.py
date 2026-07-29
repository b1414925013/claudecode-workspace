"""pyhutool.json - JSON 处理模块（依赖 orjson）。

对齐 Hutool 的 ``cn.hutool.json.JSONUtil``。底层使用 ``orjson`` 实现高性能
序列化/反序列化，文件 I/O 委托给 ``pyhutool.io.FileUtil`` 以复用统一的
路径处理与异常包装。

注意：``orjson`` 是可选依赖。若未安装，调用本模块任何方法都会抛
``UtilError``，提示用户 ``pip install "pyhutool[json]"``。
"""

from pyhutool.json.json_util import JsonUtil

__all__ = ["JsonUtil"]
