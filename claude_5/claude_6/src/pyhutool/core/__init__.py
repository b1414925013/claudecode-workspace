"""pyhutool.core - 核心工具模块（零依赖）。

对齐 Hutool 的 ``cn.hutool.core`` 包，提供字符串、对象、集合、日期、
数值等高频工具。本模块仅依赖 Python 标准库。
"""

from pyhutool.core.coll_util import CollUtil
from pyhutool.core.date_util import DateField, DateUnit, DateUtil
from pyhutool.core.exceptions import PyHutoolError, StateError, UtilError
from pyhutool.core.id_util import IdUtil
from pyhutool.core.num_util import NumUtil
from pyhutool.core.object_util import ObjectUtil
from pyhutool.core.random_util import RandomUtil
from pyhutool.core.regex_util import RegexUtil
from pyhutool.core.str_util import StrUtil

__all__ = [
    "CollUtil",
    "DateField",
    "DateUnit",
    "DateUtil",
    "IdUtil",
    "NumUtil",
    "ObjectUtil",
    "PyHutoolError",
    "RandomUtil",
    "RegexUtil",
    "StateError",
    "StrUtil",
    "UtilError",
]
