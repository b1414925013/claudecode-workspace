"""日期时间工具。

对齐 Hutool 的 ``cn.hutool.core.date.DateUtil``，提供日期解析、格式化、
偏移、区间计算等高频操作。

与 Hutool 的差异：
- 日期类型使用 Python ``datetime.datetime``；
- 模式串支持 Java ``SimpleDateFormat`` 风格（如 ``yyyy-MM-dd HH:mm:ss``），
  内部自动转换为 Python ``strftime`` 模式，便于 API 对齐。
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from enum import IntEnum

__all__ = ["DateField", "DateUnit", "DateUtil"]


class DateField(IntEnum):
    """日期字段枚举，对应 Hutool ``DateField``。"""

    YEAR = 1
    MONTH = 2
    WEEK_OF_YEAR = 3
    WEEK_OF_MONTH = 4
    DAY_OF_MONTH = 5
    DAY_OF_YEAR = 6
    DAY_OF_WEEK = 7
    HOUR_OF_DAY = 8
    MINUTE = 9
    SECOND = 10
    MILLISECOND = 11


class DateUnit(IntEnum):
    """时间单位枚举，对应 Hutool ``DateUnit``。"""

    MS = 1
    SECOND = 2
    MINUTE = 3
    HOUR = 4
    DAY = 5
    WEEK = 6


# Java SimpleDateFormat token → Python strftime（按长度降序匹配）
_JAVA_TOKENS: list[tuple[str, str]] = [
    ("yyyy", "%Y"),
    ("yyy", "%Y"),
    ("yy", "%y"),
    ("MMMM", "%B"),
    ("MMM", "%b"),
    ("MM", "%m"),
    ("dd", "%d"),
    ("HH", "%H"),
    ("mm", "%M"),
    ("ss", "%S"),
    ("SSS", "%f"),
    ("SS", "%f"),
    ("S", "%f"),
    ("EEEE", "%A"),
    ("EEE", "%a"),
    ("a", "%p"),
    ("Z", "%z"),
]


def _java_to_python_pattern(pattern: str) -> str:
    """将 Java SimpleDateFormat 模式转换为 Python strftime 模式。

    仅识别常用 token，未识别的字符原样保留。
    """
    out: list[str] = []
    i = 0
    n = len(pattern)
    while i < n:
        matched = False
        for java_tok, py_tok in _JAVA_TOKENS:
            if pattern.startswith(java_tok, i):
                out.append(py_tok)
                i += len(java_tok)
                matched = True
                break
        if not matched:
            out.append(pattern[i])
            i += 1
    return "".join(out)


class DateUtil:
    """日期时间工具类，全部为静态方法。"""

    DEFAULT_PATTERN = "yyyy-MM-dd HH:mm:ss"
    DATE_PATTERN = "yyyy-MM-dd"
    TIME_PATTERN = "HH:mm:ss"

    # ------------------------------------------------------------------
    # 当前时间
    # ------------------------------------------------------------------
    @staticmethod
    def date() -> datetime:
        """返回当前时间。"""
        return datetime.now()

    @staticmethod
    def date_second() -> datetime:
        """返回当前时间，秒级精度（截断到秒）。"""
        now = datetime.now()
        return now.replace(microsecond=0)

    @staticmethod
    def now() -> str:
        """返回当前时间的字符串表示，格式 ``yyyy-MM-dd HH:mm:ss``。"""
        return DateUtil.format_datetime(datetime.now())

    @staticmethod
    def today() -> str:
        """返回今天的日期字符串，格式 ``yyyy-MM-dd``。"""
        return DateUtil.format_date(datetime.now())

    @staticmethod
    def current() -> int:
        """返回当前时间的毫秒时间戳。"""
        return int(datetime.now().timestamp() * 1000)

    # ------------------------------------------------------------------
    # 格式化
    # ------------------------------------------------------------------
    @staticmethod
    def format(date: datetime | None, pattern: str = DEFAULT_PATTERN) -> str:
        """按 Java 模式格式化日期。``None`` 返回空串。"""
        if date is None:
            return ""
        return date.strftime(_java_to_python_pattern(pattern))

    @staticmethod
    def format_date(date: datetime | None, pattern: str = DATE_PATTERN) -> str:
        """按 ``yyyy-MM-dd`` 格式化。"""
        return DateUtil.format(date, pattern)

    @staticmethod
    def format_datetime(date: datetime | None, pattern: str = DEFAULT_PATTERN) -> str:
        """按 ``yyyy-MM-dd HH:mm:ss`` 格式化。"""
        return DateUtil.format(date, pattern)

    @staticmethod
    def format_time(date: datetime | None, pattern: str = TIME_PATTERN) -> str:
        """按 ``HH:mm:ss`` 格式化。"""
        return DateUtil.format(date, pattern)

    # ------------------------------------------------------------------
    # 解析
    # ------------------------------------------------------------------
    @staticmethod
    def parse(text: str, pattern: str = DEFAULT_PATTERN) -> datetime:
        """按 Java 模式解析字符串为 ``datetime``。"""
        return datetime.strptime(text, _java_to_python_pattern(pattern))

    @staticmethod
    def parse_date(text: str) -> datetime:
        """解析 ``yyyy-MM-dd`` 字符串。"""
        return DateUtil.parse(text, DateUtil.DATE_PATTERN)

    @staticmethod
    def parse_datetime(text: str) -> datetime:
        """解析 ``yyyy-MM-dd HH:mm:ss`` 字符串。"""
        return DateUtil.parse(text, DateUtil.DEFAULT_PATTERN)

    @staticmethod
    def parse_utc(text: str) -> datetime:
        """解析 ISO 8601 / UTC 字符串（如 ``2026-01-01T12:00:00+08:00``）。"""
        return datetime.fromisoformat(text)

    # ------------------------------------------------------------------
    # 时间戳
    # ------------------------------------------------------------------
    @staticmethod
    def to_epoch_ms(date: datetime) -> int:
        """转换为毫秒时间戳。"""
        return int(date.timestamp() * 1000)

    @staticmethod
    def to_epoch_sec(date: datetime) -> int:
        """转换为秒时间戳。"""
        return int(date.timestamp())

    @staticmethod
    def from_epoch_ms(ms: int) -> datetime:
        """由毫秒时间戳构造 ``datetime``。"""
        return datetime.fromtimestamp(ms / 1000.0)

    @staticmethod
    def from_epoch_sec(sec: int) -> datetime:
        """由秒时间戳构造 ``datetime``。"""
        return datetime.fromtimestamp(sec)

    # ------------------------------------------------------------------
    # 偏移
    # ------------------------------------------------------------------
    @staticmethod
    def offset(date: datetime, field: DateField, amount: int) -> datetime:
        """对指定字段进行偏移。"""
        if field == DateField.YEAR:
            return date.replace(year=date.year + amount)
        if field == DateField.MONTH:
            total = date.month - 1 + amount
            year = date.year + total // 12
            month = total % 12 + 1
            return date.replace(year=year, month=month)
        if field == DateField.DAY_OF_MONTH:
            return date + timedelta(days=amount)
        if field == DateField.HOUR_OF_DAY:
            return date + timedelta(hours=amount)
        if field == DateField.MINUTE:
            return date + timedelta(minutes=amount)
        if field == DateField.SECOND:
            return date + timedelta(seconds=amount)
        if field == DateField.MILLISECOND:
            return date + timedelta(milliseconds=amount)
        if field == DateField.WEEK_OF_YEAR:
            return date + timedelta(weeks=amount)
        raise ValueError(f"不支持的字段: {field}")

    @staticmethod
    def offset_day(date: datetime, days: int) -> datetime:
        """按天偏移。"""
        return date + timedelta(days=days)

    @staticmethod
    def offset_hour(date: datetime, hours: int) -> datetime:
        """按小时偏移。"""
        return date + timedelta(hours=hours)

    @staticmethod
    def offset_minute(date: datetime, minutes: int) -> datetime:
        """按分钟偏移。"""
        return date + timedelta(minutes=minutes)

    # ------------------------------------------------------------------
    # 区间边界
    # ------------------------------------------------------------------
    @staticmethod
    def begin_of_day(date: datetime) -> datetime:
        """返回当天的开始（00:00:00）。"""
        return date.replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def end_of_day(date: datetime) -> datetime:
        """返回当天的结束（23:59:59.999999）。"""
        return date.replace(hour=23, minute=59, second=59, microsecond=999999)

    @staticmethod
    def begin_of_month(date: datetime) -> datetime:
        """返回当月的开始。"""
        return date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def end_of_month(date: datetime) -> datetime:
        """返回当月的结束（最后一天 23:59:59.999999）。"""
        # 下个月第一天 - 1 微秒
        if date.month == 12:
            next_first = date.replace(year=date.year + 1, month=1, day=1)
        else:
            next_first = date.replace(month=date.month + 1, day=1)
        return next_first.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(
            microseconds=1
        )

    # ------------------------------------------------------------------
    # 取值
    # ------------------------------------------------------------------
    @staticmethod
    def day_of_week(date: datetime) -> int:
        """返回星期几，``1=周日, 2=周一, ..., 7=周六``（与 Java ``Calendar`` 一致）。"""
        # Python: Monday=0..Sunday=6
        py_dow = date.weekday()
        return ((py_dow + 1) % 7) + 1

    @staticmethod
    def day_of_month(date: datetime) -> int:
        """返回月份中的第几天。"""
        return date.day

    @staticmethod
    def day_of_year(date: datetime) -> int:
        """返回年份中的第几天。"""
        return date.timetuple().tm_yday

    @staticmethod
    def is_leap_year(year: int) -> bool:
        """判断是否为闰年。"""
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    # ------------------------------------------------------------------
    # 比较 / 区间
    # ------------------------------------------------------------------
    @staticmethod
    def is_same_day(d1: datetime, d2: datetime) -> bool:
        """判断两个日期是否为同一天。"""
        return d1.date() == d2.date()

    @staticmethod
    def between(d1: datetime, d2: datetime, unit: DateUnit) -> int:
        """计算两个时间之间的差值（取绝对值）。"""
        delta = abs(d2 - d1)
        if unit == DateUnit.MS:
            return int(delta.total_seconds() * 1000)
        if unit == DateUnit.SECOND:
            return int(delta.total_seconds())
        if unit == DateUnit.MINUTE:
            return int(delta.total_seconds() // 60)
        if unit == DateUnit.HOUR:
            return int(delta.total_seconds() // 3600)
        if unit == DateUnit.DAY:
            return int(delta.total_seconds() // 86400)
        if unit == DateUnit.WEEK:
            return int(delta.total_seconds() // (86400 * 7))
        raise ValueError(f"不支持的单位: {unit}")

    @staticmethod
    def between_ms(d1: datetime, d2: datetime) -> int:
        """毫秒差。"""
        return DateUtil.between(d1, d2, DateUnit.MS)

    @staticmethod
    def between_second(d1: datetime, d2: datetime) -> int:
        """秒差。"""
        return DateUtil.between(d1, d2, DateUnit.SECOND)

    @staticmethod
    def between_day(d1: datetime, d2: datetime) -> int:
        """天差。"""
        return DateUtil.between(d1, d2, DateUnit.DAY)

    # ------------------------------------------------------------------
    # 时区
    # ------------------------------------------------------------------
    @staticmethod
    def to_utc(date: datetime) -> datetime:
        """将带时区的 datetime 转换为 UTC（无时区信息时视为本地时间）。"""
        if date.tzinfo is None:
            date = date.astimezone()
        return date.astimezone(UTC)

    @staticmethod
    def of_utc(
        year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0
    ) -> datetime:
        """构造 UTC 时间。"""
        return datetime(year, month, day, hour, minute, second, tzinfo=UTC)
