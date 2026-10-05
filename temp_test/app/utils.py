# -*- coding: utf-8 -*-
"""
命名转换与日期时间解析工具函数
"""
import re
from datetime import datetime, timezone
from typing import Tuple


# ─── 命名转换工具 ──────────────────────────────────────────────────────────────

def split_words(text: str) -> list[str]:
    """把任意输入文本拆分成单词列表。

    支持：空格、下划线、横杠、点等分隔符；
    驼峰边界（helloWorld -> hello World）；
    连续大写缩写（HTTPServer -> HTTP Server）；
    字母与数字边界（user2Name -> user 2 Name）。
    """
    normalized = re.sub(r"[_\-.\\/]+", " ", text.strip())
    words: list[str] = []
    pattern = r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|\d+"
    for segment in normalized.split():
        words.extend(re.findall(pattern, segment))
    return words


def to_camel(words: list[str]) -> str:
    """生成小驼峰：首单词全小写，其余单词首字母大写。"""
    if not words:
        return ""
    head = words[0].lower()
    rest = "".join(w.capitalize() for w in words[1:])
    return head + rest


# ─── 时间戳工具 ────────────────────────────────────────────────────────────────

_MS_BOUNDARY = 10**11
_US_BOUNDARY = 10**14
_WEEKDAYS_CN = ("星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日")


def guess_unit(ts: int) -> str:
    """按时间戳量级猜测单位：秒 / 毫秒 / 微秒。"""
    if abs(ts) >= _US_BOUNDARY:
        return "microseconds"
    if abs(ts) >= _MS_BOUNDARY:
        return "milliseconds"
    return "seconds"


def ts_to_datetime(ts: int) -> Tuple[datetime, str]:
    """把时间戳换算为 UTC datetime，自动识别秒/毫秒/微秒。"""
    unit = guess_unit(ts)
    if unit == "milliseconds":
        dt_utc = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    elif unit == "microseconds":
        dt_utc = datetime.fromtimestamp(ts / 1_000_000, tz=timezone.utc)
    else:
        dt_utc = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt_utc, unit


def parse_date_text(text: str) -> datetime:
    """把常见格式的日期文本解析为 datetime。

    支持：
        2026-10-04、2026/10/4（仅日期，横杠/斜杠均可）
        2026-10-04 12:30、2026-10-04 12:30:00（日期 + 时间）
        2026-10-04T12:30:00（ISO 8601，可含 Z 或 ±hh:mm 时区后缀）
    """
    cleaned = text.strip().replace("/", "-")
    try:
        return datetime.fromisoformat(cleaned)
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    raise ValueError(f"无法识别的日期格式: {text!r}")
