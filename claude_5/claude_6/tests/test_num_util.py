"""NumUtil 单元测试。"""

from __future__ import annotations

from decimal import Decimal

import pytest

from pyhutool.core import NumUtil


class TestArithmetic:
    """算术。"""

    def test_add(self) -> None:
        assert NumUtil.add(0.1, 0.2) == Decimal("0.3")
        assert NumUtil.add(1, 2, 3) == Decimal(6)
        assert NumUtil.add() == Decimal(0)

    def test_sub(self) -> None:
        assert NumUtil.sub(10, 3) == Decimal(7)
        assert NumUtil.sub(10, 3, 2) == Decimal(5)
        assert NumUtil.sub() == Decimal(0)

    def test_mul(self) -> None:
        assert NumUtil.mul(2, 3, 4) == Decimal(24)
        assert NumUtil.mul("0.1", "0.2") == Decimal("0.02")

    def test_div(self) -> None:
        assert NumUtil.div(10, 4, scale=2) == Decimal("2.50")
        assert NumUtil.div(1, 3, scale=2) == Decimal("0.33")

    def test_div_by_zero(self) -> None:
        with pytest.raises(ZeroDivisionError):
            NumUtil.div(1, 0)


class TestRound:
    """四舍五入。"""

    def test_round(self) -> None:
        assert NumUtil.round(3.14159, 2) == Decimal("3.14")
        assert NumUtil.round(3.145, 2) == Decimal("3.15")
        assert NumUtil.round(3.14159, 0) == Decimal("3")

    def test_round_str(self) -> None:
        assert NumUtil.round_str(3.14159, 2) == "3.14"


class TestDecimalFormat:
    """decimal_format。"""

    def test_basic(self) -> None:
        assert NumUtil.decimal_format(3.14159, "0.00") == "3.14"
        assert NumUtil.decimal_format(3.1, "0.00") == "3.10"

    def test_optional_frac(self) -> None:
        assert NumUtil.decimal_format(3.14159, "0.##") == "3.14"
        assert NumUtil.decimal_format(3.1, "0.##") == "3.1"

    def test_no_fraction(self) -> None:
        assert NumUtil.decimal_format(3.99, "0") == "4"


class TestCheck:
    """判断。"""

    def test_is_number(self) -> None:
        assert NumUtil.is_number("123") is True
        assert NumUtil.is_number("-1.5") is True
        assert NumUtil.is_number("1e10") is True
        assert NumUtil.is_number("abc") is False
        assert NumUtil.is_number(123) is True
        assert NumUtil.is_number(True) is True

    def test_is_integer(self) -> None:
        assert NumUtil.is_integer("123") is True
        assert NumUtil.is_integer("12.3") is False
        assert NumUtil.is_integer(12.0) is True
        assert NumUtil.is_integer(12.5) is False
        assert NumUtil.is_integer(Decimal("3")) is True
        assert NumUtil.is_integer(Decimal("3.5")) is False


class TestConvert:
    """转换。"""

    def test_to_int(self) -> None:
        assert NumUtil.to_int("123") == 123
        assert NumUtil.to_int("12.9") == 12
        assert NumUtil.to_int("abc", -1) == -1

    def test_to_long(self) -> None:
        assert NumUtil.to_long("9999999999") == 9999999999

    def test_to_double(self) -> None:
        assert NumUtil.to_double("3.14") == pytest.approx(3.14)
        assert NumUtil.to_double("x", 0.0) == 0.0

    def test_to_str(self) -> None:
        assert NumUtil.to_str(Decimal("3.14")) == "3.14"
        assert NumUtil.to_str(3) == "3"

    def test_null_to_zero(self) -> None:
        assert NumUtil.null_to_zero(None) == Decimal(0)
        assert NumUtil.null_to_zero("5") == Decimal(5)
        assert NumUtil.null_to_zero("abc") == Decimal(0)


class TestExtremum:
    """极值。"""

    def test_max_min(self) -> None:
        assert NumUtil.max(1, 2, 3) == Decimal(3)
        assert NumUtil.min(1, 2, 3) == Decimal(1)


def test_decimal_precision() -> None:
    """关键精度特性：浮点误差消除。"""
    result = NumUtil.add(0.1, 0.2)
    assert float(result) == 0.3
