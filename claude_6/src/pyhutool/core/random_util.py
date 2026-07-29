"""随机工具。

对齐 Hutool 的 ``cn.hutool.core.util.RandomUtil``，提供随机数、随机元素、
随机字符串等。内部使用 Python ``random`` 模块
（Hutool 使用 ``ThreadLocalRandom``）。
"""

from __future__ import annotations

import random
import string
from collections.abc import Sequence
from typing import TypeVar

__all__ = ["RandomUtil"]

T = TypeVar("T")

# 字符表
_LOWERS = string.ascii_lowercase
_UPPERS = string.ascii_uppercase
_DIGITS = string.digits
_ALPHAS = string.ascii_letters + string.digits


class RandomUtil:
    """随机工具类，全部为静态方法。"""

    # ------------------------------------------------------------------
    # 随机数
    # ------------------------------------------------------------------
    @staticmethod
    def random_int(start: int, end: int) -> int:
        """返回 ``[start, end)`` 区间的随机整数。"""
        if end <= start:
            raise ValueError("end 必须大于 start")
        return random.randint(start, end - 1)

    @staticmethod
    def random_int_with_range(start: int, end: int) -> int:
        """返回 ``[start, end]`` 闭区间的随机整数（对应 Hutool randomInt 闭区间版本）。"""
        return random.randint(start, end)

    @staticmethod
    def random_long(start: int, end: int) -> int:
        """返回 ``[start, end)`` 区间的随机长整型（Python 即 ``int``）。"""
        return RandomUtil.random_int(start, end)

    @staticmethod
    def random_double(start: float, end: float) -> float:
        """返回 ``[start, end)`` 区间的随机浮点数。"""
        if end <= start:
            raise ValueError("end 必须大于 start")
        return random.uniform(start, end)

    @staticmethod
    def random_boolean() -> bool:
        """随机布尔值。"""
        return random.choice([True, False])

    @staticmethod
    def random_char(base: str = _ALPHAS) -> str:
        """从给定字符表中随机取一个字符。"""
        if not base:
            raise ValueError("base 不能为空")
        return random.choice(base)

    # ------------------------------------------------------------------
    # 随机元素
    # ------------------------------------------------------------------
    @staticmethod
    def random_ele(seq: Sequence[T]) -> T:
        """从序列中随机取一个元素。空序列抛出 ``IndexError``。"""
        if len(seq) == 0:
            raise IndexError("序列不能为空")
        return random.choice(seq)

    @staticmethod
    def random_els(seq: Sequence[T], count: int) -> list[T]:
        """从序列中随机取 ``count`` 个元素（允许重复）。"""
        if count <= 0:
            return []
        return [random.choice(seq) for _ in range(count)]

    @staticmethod
    def random_els_distinct(seq: Sequence[T], count: int) -> list[T]:
        """从序列中随机取 ``count`` 个不重复元素。"""
        if count > len(seq):
            raise ValueError("count 不能超过序列长度")
        return random.sample(list(seq), count)

    # ------------------------------------------------------------------
    # 随机字符串
    # ------------------------------------------------------------------
    @staticmethod
    def random_string(length: int) -> str:
        """随机字母+数字字符串。"""
        if length <= 0:
            return ""
        return "".join(random.choices(_ALPHAS, k=length))

    @staticmethod
    def random_lower_string(length: int) -> str:
        """随机小写字母+数字字符串。"""
        if length <= 0:
            return ""
        base = _LOWERS + _DIGITS
        return "".join(random.choices(base, k=length))

    @staticmethod
    def random_numbers(length: int) -> str:
        """随机数字字符串。"""
        if length <= 0:
            return ""
        return "".join(random.choices(_DIGITS, k=length))

    @staticmethod
    def random_upper_string(length: int) -> str:
        """随机大写字母+数字字符串。"""
        if length <= 0:
            return ""
        base = _UPPERS + _DIGITS
        return "".join(random.choices(base, k=length))

    # ------------------------------------------------------------------
    # 种子
    # ------------------------------------------------------------------
    @staticmethod
    def seed(seed: int | float | str | bytes | bytearray | None = None) -> random.Random:
        """返回一个带种子的独立 ``random.Random`` 实例，避免污染全局状态。"""
        return random.Random(seed)
