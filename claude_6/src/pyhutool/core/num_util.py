"""数值工具。

对齐 Hutool 的 ``cn.hutool.core.util.NumberUtil``，提供加减乘除、四舍五入、
类型转换等运算。算术运算内部使用 ``decimal.Decimal`` 保证精度
（对应 Hutool 使用 ``BigDecimal``）。
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation, getcontext
from typing import Any

__all__ = ["NumUtil"]

# 运算默认保留小数位数
_DEFAULT_SCALE = 2
# 除法默认舍入模式：四舍五入
_ROUND = None  # 使用 ROUND_HALF_UP


def _to_decimal(value: Any) -> Decimal:
    """将任意数值/字符串转换为 ``Decimal``。"""
    if isinstance(value, Decimal):
        return value
    if isinstance(value, bool):
        return Decimal(int(value))
    if isinstance(value, (int, float)):
        # float 走 str 路径避免二进制误差
        return Decimal(str(value))
    return Decimal(str(value))


class NumUtil:
    """数值工具类，全部为静态方法。"""

    # ------------------------------------------------------------------
    # 算术（对应 Hutool add / sub / mul / div）
    # ------------------------------------------------------------------
    @staticmethod
    def add(*values: Any) -> Decimal:
        """求和，内部使用 ``Decimal`` 避免浮点误差。"""
        result = Decimal(0)
        for v in values:
            result += _to_decimal(v)
        return result

    @staticmethod
    def sub(*values: Any) -> Decimal:
        """依次相减。至少需两个值。"""
        if len(values) < 1:
            return Decimal(0)
        result = _to_decimal(values[0])
        for v in values[1:]:
            result -= _to_decimal(v)
        return result

    @staticmethod
    def mul(*values: Any) -> Decimal:
        """连乘。"""
        result = Decimal(1)
        for v in values:
            result *= _to_decimal(v)
        return result

    @staticmethod
    def div(a: Any, b: Any, scale: int = _DEFAULT_SCALE) -> Decimal:
        """除法，``b`` 为 0 抛出 ``ZeroDivisionError``。"""
        divisor = _to_decimal(b)
        if divisor == 0:
            raise ZeroDivisionError("除数不能为 0")
        from decimal import ROUND_HALF_UP

        return (_to_decimal(a) / divisor).quantize(Decimal(10) ** (-scale), rounding=ROUND_HALF_UP)

    # ------------------------------------------------------------------
    # 四舍五入
    # ------------------------------------------------------------------
    @staticmethod
    def round(value: Any, scale: int = _DEFAULT_SCALE) -> Decimal:
        """四舍五入到指定小数位。"""
        from decimal import ROUND_HALF_UP

        return _to_decimal(value).quantize(Decimal(10) ** (-scale), rounding=ROUND_HALF_UP)

    @staticmethod
    def round_str(value: Any, scale: int = _DEFAULT_SCALE) -> str:
        """四舍五入并返回字符串。"""
        return str(NumUtil.round(value, scale))

    @staticmethod
    def decimal_format(value: Any, pattern: str = "0.00") -> str:
        """按 Java ``DecimalFormat`` 风格格式化数字。

        支持 ``0``（必填位）、``#``（可选位）与小数点。例如 ``0.##``。
        """
        from decimal import ROUND_HALF_UP

        frac_part = pattern.split(".", 1)[1] if "." in pattern else ""
        # 小数位：# 计数到末尾连续 0/#，按 0 个数固定 + # 可选
        required = frac_part.count("0")
        optional = frac_part.count("#")
        d = _to_decimal(value)
        if required + optional > 0:
            d = d.quantize(Decimal(10) ** (-(required + optional)), rounding=ROUND_HALF_UP)
            s = f"{d:.{required + optional}f}"
            # 裁剪末尾多余的 0，但至少保留 required 位
            if optional > 0 and "." in s:
                int_s, frac_s = s.split(".", 1)
                frac_s = frac_s[:required] + frac_s[required:].rstrip("0")
                s = f"{int_s}.{frac_s}" if frac_s else int_s
        else:
            # 无小数位时四舍五入到整数（Java DecimalFormat 语义）
            s = str(int(d.to_integral_value(rounding=ROUND_HALF_UP)))
        return s

    # ------------------------------------------------------------------
    # 判断
    # ------------------------------------------------------------------
    @staticmethod
    def is_number(value: Any) -> bool:
        """判断是否为合法数字（字符串或数值）。"""
        if isinstance(value, bool):
            return True
        if isinstance(value, (int, float, Decimal)):
            return True
        if isinstance(value, str):
            return bool(re.fullmatch(r"-?\d+(\.\d+)?([eE][+-]?\d+)?", value.strip()))
        return False

    @staticmethod
    def is_integer(value: Any) -> bool:
        """判断是否为整数。"""
        if isinstance(value, bool):
            return True
        if isinstance(value, int):
            return True
        if isinstance(value, float):
            return value.is_integer()
        if isinstance(value, Decimal):
            return value == value.to_integral_value()
        if isinstance(value, str):
            return bool(re.fullmatch(r"-?\d+", value.strip()))
        return False

    @staticmethod
    def null_to_zero(value: Any) -> Decimal:
        """``None`` 或空值转为 0。"""
        if value is None:
            return Decimal(0)
        try:
            return _to_decimal(value)
        except (InvalidOperation, ValueError):
            return Decimal(0)

    # ------------------------------------------------------------------
    # 转换
    # ------------------------------------------------------------------
    @staticmethod
    def to_int(value: Any, default: int = 0) -> int:
        """转为 int，失败返回 ``default``。"""
        try:
            return int(_to_decimal(value))
        except (InvalidOperation, ValueError, TypeError):
            return default

    @staticmethod
    def to_long(value: Any, default: int = 0) -> int:
        """转为长整型（Python ``int`` 即可表示）。"""
        return NumUtil.to_int(value, default)

    @staticmethod
    def to_double(value: Any, default: float = 0.0) -> float:
        """转为 float，失败返回 ``default``。"""
        try:
            return float(_to_decimal(value))
        except (InvalidOperation, ValueError, TypeError):
            return default

    @staticmethod
    def to_str(value: Any) -> str:
        """转为字符串。"""
        if isinstance(value, Decimal):
            return str(value)
        return str(value)

    # ------------------------------------------------------------------
    # 极值
    # ------------------------------------------------------------------
    @staticmethod
    def max(*values: Any) -> Decimal:
        """返回最大值。"""
        decimals = [_to_decimal(v) for v in values]
        return max(decimals)

    @staticmethod
    def min(*values: Any) -> Decimal:
        """返回最小值。"""
        decimals = [_to_decimal(v) for v in values]
        return min(decimals)


# 设置 Decimal 默认精度上限，避免除法无限循环
getcontext().prec = 50
