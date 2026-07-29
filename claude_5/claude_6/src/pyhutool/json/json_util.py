"""JSON 工具。

对齐 Hutool 的 ``cn.hutool.json.JSONUtil``，提供 JSON 解析、序列化、
文件读写、格式校验、转义等高频操作。底层基于 ``orjson`` 实现。

设计说明
--------
- ``orjson`` 是可选依赖；未安装时本模块所有方法抛 ``UtilError``；
- Python 自带 ``dict`` / ``list`` 已是首选容器，本模块不再包装为
  ``JSONObject`` / ``JSONArray``，而是直接返回原生类型；
- 文件 I/O 委托 ``pyhutool.io.FileUtil``，行为与 ``IoUtil`` 一致；
- orjson 默认 ``ensure_ascii=False``（与 Hutool 行为一致，中文不转义）。
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Final, cast

from pyhutool.core.exceptions import UtilError

__all__ = ["JsonUtil"]

_UTF8: Final[str] = "UTF-8"

# 匹配任意反斜杠序列：``\\uXXXX`` / ``\\X``（X 为简单转义字符或任意字符）
# 第 1 组用于判断是合法还是非法转义
_JSON_ESCAPE_RE: Final[re.Pattern[str]] = re.compile(
    r"\\(u[0-9a-fA-F]{4}|[\"\\/bfnrt]|.)",
    re.DOTALL,
)

# 简单转义字符映射
_SIMPLE_ESCAPES: Final[dict[str, str]] = {
    '"': '"',
    "\\": "\\",
    "/": "/",
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
}


def _require_orjson() -> Any:
    """惰性导入 ``orjson``；未安装时抛 ``UtilError``。"""
    try:
        import orjson
    except ImportError as e:
        raise UtilError(
            "pyhutool.json 需要 orjson 支持，请运行：pip install 'pyhutool[json]'",
            cause=e,
        ) from e
    return orjson


def _default_hook(obj: Any) -> Any:
    """orjson 默认对象转换钩子：把无法识别的对象转成 ``str``。"""
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return str(obj)


class JsonUtil:
    """JSON 工具类，全部为静态方法。

    对应 Hutool ``cn.hutool.json.JSONUtil``。
    """

    # ------------------------------------------------------------------
    # 解析
    # ------------------------------------------------------------------
    @staticmethod
    def parse(text: str | bytes) -> Any:
        """解析 JSON 字符串/字节为 Python 对象（dict/list/str/int/...）。

        对应 Hutool ``JSONUtil.parse``。
        """
        orjson = _require_orjson()
        try:
            return orjson.loads(text)
        except orjson.JSONDecodeError as e:
            raise UtilError("JSON 解析失败", cause=e) from e

    @staticmethod
    def parse_obj(text: str | bytes) -> dict[str, Any]:
        """解析为 ``dict``。非对象类型将抛 ``UtilError``。"""
        result = JsonUtil.parse(text)
        if not isinstance(result, dict):
            raise UtilError(f"期望 JSON 对象，但解析得到: {type(result).__name__}")
        return result

    @staticmethod
    def parse_array(text: str | bytes) -> list[Any]:
        """解析为 ``list``。非数组类型将抛 ``UtilError``。"""
        result = JsonUtil.parse(text)
        if not isinstance(result, list):
            raise UtilError(f"期望 JSON 数组，但解析得到: {type(result).__name__}")
        return result

    # ------------------------------------------------------------------
    # 序列化
    # ------------------------------------------------------------------
    @staticmethod
    def to_json_str(
        obj: Any,
        indent: int | None = None,
        sort_keys: bool = False,
    ) -> str:
        """把 Python 对象序列化为 JSON 字符串。

        对应 Hutool ``JSONUtil.toJsonStr``。

        Parameters
        ----------
        obj:
            任意可序列化对象。``datetime`` / ``Decimal`` / ``dataclass``
            等类型 ``orjson`` 原生支持；自定义类型会退化为 ``str``。
        indent:
            缩进空格数；``None`` 表示紧凑输出。仅支持 ``2``（orjson 限制），
            传入其他正整数会被规整为 ``2``。
        sort_keys:
            是否按键名字典序排序。
        """
        orjson = _require_orjson()
        opts = 0
        if indent is not None:
            opts |= orjson.OPT_INDENT_2
        if sort_keys:
            opts |= orjson.OPT_SORT_KEYS
        try:
            payload = cast(
                bytes,
                orjson.dumps(
                    obj,
                    default=_default_hook,
                    option=opts,
                ),
            )
        except (orjson.JSONEncodeError, TypeError) as e:
            raise UtilError("JSON 序列化失败", cause=e) from e
        return payload.decode(_UTF8)

    @staticmethod
    def pretty_format(text: str | bytes) -> str:
        """美化 JSON 字符串（紧凑或已有缩进均可）。返回带缩进的字符串。

        对应 Hutool ``JSONUtil.formatJsonStr``。
        """
        obj = JsonUtil.parse(text)
        return JsonUtil.to_json_str(obj, indent=2)

    # ------------------------------------------------------------------
    # 文件读写
    # ------------------------------------------------------------------
    @staticmethod
    def read_json_file(
        path: str | Path,
        charset: str = _UTF8,
    ) -> Any:
        """读取文件并解析为 Python 对象。

        对应 Hutool ``JSONUtil.readJSON``。
        """
        from pyhutool.io import FileUtil

        text = FileUtil.read_string(path, charset=charset)
        return JsonUtil.parse(text)

    @staticmethod
    def write_json_file(
        obj: Any,
        path: str | Path,
        indent: int | None = None,
        sort_keys: bool = False,
        append: bool = False,
    ) -> int:
        """把对象序列化为 JSON 并写入文件。

        对应 Hutool ``JSONUtil.writeJSONString`` (File 重载)。
        """
        from pyhutool.io import FileUtil

        text = JsonUtil.to_json_str(obj, indent=indent, sort_keys=sort_keys)
        return FileUtil.write_utf8(text, path, append=append)

    # ------------------------------------------------------------------
    # 类型判断
    # ------------------------------------------------------------------
    @staticmethod
    def is_json(text: str | bytes | None) -> bool:
        """判断字符串是否为合法 JSON（对象或数组）。"""
        if not text:
            return False
        try:
            result = JsonUtil.parse(text)
        except UtilError:
            return False
        return isinstance(result, (dict, list))

    @staticmethod
    def is_json_object(text: str | bytes | None) -> bool:
        """判断字符串是否为合法 JSON 对象（``{...}``）。"""
        if not text:
            return False
        try:
            result = JsonUtil.parse(text)
        except UtilError:
            return False
        return isinstance(result, dict)

    @staticmethod
    def is_json_array(text: str | bytes | None) -> bool:
        """判断字符串是否为合法 JSON 数组（``[...]``）。"""
        if not text:
            return False
        try:
            result = JsonUtil.parse(text)
        except UtilError:
            return False
        return isinstance(result, list)

    # ------------------------------------------------------------------
    # 转义
    # ------------------------------------------------------------------
    @staticmethod
    def escape(text: str | None) -> str:
        """转义字符串中的特殊字符（``\\"`` ``\\\\`` ``\\n`` ``\\t`` 等）。

        对应 Hutool ``JSONUtil.escape``。与 ``json.dumps`` 不同，本方法
        不会在外侧加引号。
        """
        if not text:
            return ""
        return text.translate(_ESCAPE_TABLE)

    @staticmethod
    def unescape(text: str | None) -> str:
        """反转义 JSON 字符串。

        对应 Hutool ``JSONUtil.unescape``。包含非法转义序列时抛 ``UtilError``。
        """
        if not text:
            return ""

        def _replace(m: re.Match[str]) -> str:
            seq = m.group(1)
            # ``\\uXXXX``
            if seq[0] == "u" and len(seq) == 5:
                return chr(int(seq[1:], 16))
            # 简单转义
            if seq in _SIMPLE_ESCAPES:
                return _SIMPLE_ESCAPES[seq]
            # 非法转义（如 ``\\x``）
            raise UtilError(f"无效的 JSON 转义序列: \\{seq}")

        return _JSON_ESCAPE_RE.sub(_replace, text)

    @staticmethod
    def quote(text: str | None) -> str:
        """用双引号包裹字符串并转义内部特殊字符。

        对应 Hutool ``JSONUtil.quote``。``None`` 返回 ``"null"``。
        """
        if text is None:
            return "null"
        return '"' + JsonUtil.escape(text) + '"'


# 转义字符映射表
_ESCAPE_TABLE: Final[dict[int, str]] = {
    ord('"'): '\\"',
    ord("\\"): "\\\\",
    ord("\n"): "\\n",
    ord("\r"): "\\r",
    ord("\t"): "\\t",
    ord("\b"): "\\b",
    ord("\f"): "\\f",
    # 控制字符 0x00-0x1F 全部用 \uXXXX 形式
    **{i: f"\\u{i:04x}" for i in range(0x20) if chr(i) not in '"\\\n\r\t\b\f'},
}
