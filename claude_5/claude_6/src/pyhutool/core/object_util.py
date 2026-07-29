"""对象工具。

对齐 Hutool 的 ``cn.hutool.core.util.ObjectUtil``，提供 ``null`` 安全判等、
默认值、克隆、空判断等通用对象操作。
"""

from __future__ import annotations

import copy
from collections.abc import Sized
from typing import Any, TypeVar

__all__ = ["ObjectUtil"]

T = TypeVar("T")

# 视为“基础类型”的类型集合：值语义，不可变，无需深拷贝
_BASIC_TYPES: tuple[type, ...] = (
    type(None),
    bool,
    int,
    float,
    complex,
    str,
    bytes,
    bytearray,
    frozenset,
    tuple,
)


class ObjectUtil:
    """对象工具类，全部为静态方法。"""

    @staticmethod
    def is_null(obj: Any) -> bool:
        """判断对象是否为 ``None``。"""
        return obj is None

    @staticmethod
    def is_not_null(obj: Any) -> bool:
        """判断对象是否非 ``None``。"""
        return obj is not None

    @staticmethod
    def default_if_null(obj: T | None, default: T) -> T:
        """若 ``obj`` 为 ``None`` 返回 ``default``，否则返回 ``obj``。"""
        return default if obj is None else obj

    @staticmethod
    def equal(obj1: Any, obj2: Any) -> bool:
        """``null`` 安全的对象相等判断。"""
        return bool(obj1 == obj2)

    @staticmethod
    def hash_code(obj: Any) -> int:
        """返回对象的哈希值，``None`` 返回 0。

        对应 Hutool ``ObjectUtil.hashCode``。
        """
        return hash(obj) if obj is not None else 0

    @staticmethod
    def to_string(obj: Any) -> str:
        """将对象转为字符串。``None`` 返回空串。"""
        return "" if obj is None else str(obj)

    @staticmethod
    def is_empty(obj: Any) -> bool:
        """判断对象是否为“空”。

        判定规则：
        - ``None`` → ``True``；
        - 字符串 → 长度为 0；
        - 其他 ``Sized`` 容器 → 长度为 0；
        - 其余对象 → ``False``。
        """
        if obj is None:
            return True
        if isinstance(obj, str):
            return len(obj) == 0
        if isinstance(obj, Sized):
            return len(obj) == 0
        return False

    @staticmethod
    def is_not_empty(obj: Any) -> bool:
        """判断对象是否非空，等价于 ``not is_empty``。"""
        return not ObjectUtil.is_empty(obj)

    @staticmethod
    def is_basic_type(obj: Any) -> bool:
        """判断对象是否为基础类型（``None``、数值、字符串、字节、不可变容器等）。"""
        return isinstance(obj, _BASIC_TYPES)

    @staticmethod
    def clone(obj: T) -> T:
        """深拷贝对象。"""
        return copy.deepcopy(obj)
