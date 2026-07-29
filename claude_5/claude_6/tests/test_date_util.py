"""DateUtil 单元测试。"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from pyhutool.core import DateField, DateUnit, DateUtil


def test_now_and_today_format() -> None:
    assert isinstance(DateUtil.now(), str)
    assert len(DateUtil.now()) == 19
    assert len(DateUtil.today()) == 10
    assert isinstance(DateUtil.current(), int)
    assert isinstance(DateUtil.date(), datetime)


def test_date_second_truncates_microseconds() -> None:
    d = DateUtil.date_second()
    assert d.microsecond == 0


def test_format_basic() -> None:
    d = datetime(2026, 7, 24, 12, 30, 45)
    assert DateUtil.format(d, "yyyy-MM-dd HH:mm:ss") == "2026-07-24 12:30:45"
    assert DateUtil.format_date(d) == "2026-07-24"
    assert DateUtil.format_time(d) == "12:30:45"
    assert DateUtil.format_datetime(d) == "2026-07-24 12:30:45"


def test_format_none_returns_empty() -> None:
    assert DateUtil.format(None) == ""


def test_parse_basic() -> None:
    d = DateUtil.parse("2026-07-24 12:30:45")
    assert d == datetime(2026, 7, 24, 12, 30, 45)
    assert DateUtil.parse_date("2026-07-24") == datetime(2026, 7, 24)
    assert DateUtil.parse_datetime("2026-01-01 00:00:00") == datetime(2026, 1, 1)


def test_parse_utc() -> None:
    d = DateUtil.parse_utc("2026-01-01T12:00:00+08:00")
    assert d.tzinfo is not None


def test_epoch_conversion() -> None:
    d = datetime(2026, 1, 1, 0, 0, 0)
    ms = DateUtil.to_epoch_ms(d)
    assert DateUtil.from_epoch_ms(ms).replace(microsecond=0) == d
    sec = DateUtil.to_epoch_sec(d)
    assert DateUtil.from_epoch_sec(sec) == d


def test_offset_year() -> None:
    d = datetime(2026, 1, 15, 10, 0, 0)
    assert DateUtil.offset(d, DateField.YEAR, 1) == datetime(2027, 1, 15, 10, 0, 0)
    assert DateUtil.offset(d, DateField.YEAR, -1) == datetime(2025, 1, 15, 10, 0, 0)


def test_offset_month_with_year_carry() -> None:
    d = datetime(2026, 11, 15, 10, 0, 0)
    assert DateUtil.offset(d, DateField.MONTH, 3) == datetime(2027, 2, 15, 10, 0, 0)
    assert DateUtil.offset(d, DateField.MONTH, -12) == datetime(2025, 11, 15, 10, 0, 0)


def test_offset_other_fields() -> None:
    d = datetime(2026, 7, 24, 10, 0, 0)
    assert DateUtil.offset(d, DateField.DAY_OF_MONTH, 5) == datetime(2026, 7, 29, 10, 0, 0)
    assert DateUtil.offset(d, DateField.HOUR_OF_DAY, 2) == datetime(2026, 7, 24, 12, 0, 0)
    assert DateUtil.offset(d, DateField.MINUTE, 30) == datetime(2026, 7, 24, 10, 30, 0)
    assert DateUtil.offset(d, DateField.SECOND, 15) == datetime(2026, 7, 24, 10, 0, 15)
    assert DateUtil.offset(d, DateField.WEEK_OF_YEAR, 1) == datetime(2026, 7, 31, 10, 0, 0)


def test_offset_shorthands() -> None:
    d = datetime(2026, 7, 24, 10, 0, 0)
    assert DateUtil.offset_day(d, 1) == datetime(2026, 7, 25, 10, 0, 0)
    assert DateUtil.offset_hour(d, 1) == datetime(2026, 7, 24, 11, 0, 0)
    assert DateUtil.offset_minute(d, 1) == datetime(2026, 7, 24, 10, 1, 0)


def test_begin_end_of_day() -> None:
    d = datetime(2026, 7, 24, 12, 30, 45, 123)
    assert DateUtil.begin_of_day(d) == datetime(2026, 7, 24, 0, 0, 0)
    assert DateUtil.end_of_day(d) == datetime(2026, 7, 24, 23, 59, 59, 999999)


def test_begin_end_of_month() -> None:
    d = datetime(2026, 2, 15, 10, 0, 0)
    assert DateUtil.begin_of_month(d) == datetime(2026, 2, 1, 0, 0, 0)
    end = DateUtil.end_of_month(d)
    assert end.day == 28  # 2026 不是闰年


def test_end_of_month_december() -> None:
    d = datetime(2026, 12, 15, 10, 0, 0)
    end = DateUtil.end_of_month(d)
    assert end.day == 31


def test_day_of_week_calendar_style() -> None:
    # 2026-01-04 是周日
    sunday = datetime(2026, 1, 4)
    assert DateUtil.day_of_week(sunday) == 1
    # 2026-01-05 是周一
    monday = datetime(2026, 1, 5)
    assert DateUtil.day_of_week(monday) == 2


def test_day_of_month_and_year() -> None:
    d = datetime(2026, 7, 24)
    assert DateUtil.day_of_month(d) == 24
    assert DateUtil.day_of_year(d) == 205  # 1月31+2月28+...+7月24


def test_is_leap_year() -> None:
    assert DateUtil.is_leap_year(2024) is True
    assert DateUtil.is_leap_year(2026) is False
    assert DateUtil.is_leap_year(2000) is True
    assert DateUtil.is_leap_year(1900) is False


def test_is_same_day() -> None:
    d1 = datetime(2026, 7, 24, 0, 0, 0)
    d2 = datetime(2026, 7, 24, 23, 59, 59)
    d3 = datetime(2026, 7, 25, 0, 0, 0)
    assert DateUtil.is_same_day(d1, d2) is True
    assert DateUtil.is_same_day(d1, d3) is False


def test_between() -> None:
    d1 = datetime(2026, 7, 24, 0, 0, 0)
    d2 = datetime(2026, 7, 24, 0, 0, 10)
    assert DateUtil.between(d1, d2, DateUnit.SECOND) == 10
    assert DateUtil.between(d1, d2, DateUnit.MS) == 10000
    d3 = datetime(2026, 7, 25, 0, 0, 0)
    assert DateUtil.between(d1, d3, DateUnit.DAY) == 1
    assert DateUtil.between(d1, d3, DateUnit.HOUR) == 24


def test_between_shorthands() -> None:
    d1 = datetime(2026, 7, 24, 0, 0, 0)
    d2 = datetime(2026, 7, 24, 0, 0, 30)
    assert DateUtil.between_second(d1, d2) == 30
    assert DateUtil.between_ms(d1, d2) == 30000


def test_to_utc() -> None:
    naive = datetime(2026, 1, 1, 12, 0, 0)
    utc = DateUtil.to_utc(naive)
    assert utc.tzinfo == UTC


def test_of_utc() -> None:
    u = DateUtil.of_utc(2026, 1, 1)
    assert u.tzinfo == UTC


def test_format_with_day_name() -> None:
    d = datetime(2026, 1, 1)
    s = DateUtil.format(d, "yyyy-MM-dd EEE")
    assert s.startswith("2026-01-01 ")


def test_offset_invalid_field_raises() -> None:
    d = datetime(2026, 1, 1)
    with pytest.raises(ValueError):
        DateUtil.offset(d, DateField.DAY_OF_WEEK, 1)
