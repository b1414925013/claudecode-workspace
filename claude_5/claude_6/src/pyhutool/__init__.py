"""pyhutool - Hutool 风格的 Python 工具库。

外部 API 对齐 Java Hutool（类名/方法名/参数语义一一对应），
内部使用 Python 3.11+ 现代特性重新实现，核心零依赖。

模块概览：
    - pyhutool.core       核心工具（零依赖，必装）
    - pyhutool.text       文本构建/Unicode（零依赖）
    - pyhutool.io         文件与流（零依赖，sync + async 双套）
    - pyhutool.http       HTTP 客户端（extra: httpx）
    - pyhutool.json       JSON 处理（extra: orjson）
    - pyhutool.crypto     加密/摘要（extra: cryptography；DigestUtil 零依赖）
    - pyhutool.jwt        JWT（extra: pyjwt）
    - pyhutool.cron       定时任务调度（extra: apscheduler）
    - pyhutool.extra.ssh  SSH 客户端（extra: paramiko）
"""

from pyhutool.core import (
    CollUtil,
    DateField,
    DateUnit,
    DateUtil,
    IdUtil,
    NumUtil,
    ObjectUtil,
    PyHutoolError,
    RandomUtil,
    RegexUtil,
    StateError,
    StrUtil,
    UtilError,
)
from pyhutool.cron import CronUtil
from pyhutool.crypto import CryptoUtil, DigestUtil
from pyhutool.extra.ssh import JschUtil
from pyhutool.http import AsyncHttpUtil, HttpResponse, HttpUtil
from pyhutool.io import AsyncFileUtil, AsyncIoUtil, FileUtil, IoUtil, ResourceUtil
from pyhutool.json import JsonUtil
from pyhutool.jwt import JWT, JWTUtil
from pyhutool.text import StringBuilder, UnicodeUtil

__version__ = "0.1.0"

__all__ = [
    "JWT",
    "AsyncFileUtil",
    "AsyncHttpUtil",
    "AsyncIoUtil",
    "CollUtil",
    "CronUtil",
    "CryptoUtil",
    "DateField",
    "DateUnit",
    "DateUtil",
    "DigestUtil",
    "FileUtil",
    "HttpResponse",
    "HttpUtil",
    "IdUtil",
    "IoUtil",
    "JWTUtil",
    "JschUtil",
    "JsonUtil",
    "NumUtil",
    "ObjectUtil",
    "PyHutoolError",
    "RandomUtil",
    "RegexUtil",
    "ResourceUtil",
    "StateError",
    "StrUtil",
    "StringBuilder",
    "UnicodeUtil",
    "UtilError",
    "__version__",
]
