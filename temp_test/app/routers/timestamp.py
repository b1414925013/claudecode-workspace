# -*- coding: utf-8 -*-
"""
时间戳转换子路由
"""
from datetime import timezone

from fastapi import APIRouter, HTTPException

from app.models import TimestampRequest, DateRequest, DateResponse, TimestampResponse
from app.utils import ts_to_datetime, parse_date_text, _WEEKDAYS_CN

router = APIRouter(prefix="/ts", tags=["时间戳转换"])


@router.post("/to-date", response_model=DateResponse, summary="时间戳转换为日期时间")
async def ts_to_date_api(req: TimestampRequest) -> DateResponse:
    """POST 接口：把秒/毫秒/微秒级时间戳换算为各格式日期时间；超范围时返回 400。"""
    try:
        dt_utc, unit = ts_to_datetime(req.timestamp)
    except (ValueError, OSError, OverflowError):
        raise HTTPException(status_code=400, detail="时间戳超出可表示范围，无法换算")
    local = dt_utc.astimezone()
    return DateResponse(
        timestamp_input=req.timestamp,
        unit=unit,
        iso_utc=dt_utc.isoformat(),
        iso_local=local.isoformat(),
        datetime_local=local.strftime("%Y-%m-%d %H:%M:%S"),
        date_only=local.strftime("%Y-%m-%d"),
        time_only=local.strftime("%H:%M:%S"),
        weekday_cn=_WEEKDAYS_CN[local.weekday()],
    )


@router.post("/to-timestamp", response_model=TimestampResponse, summary="日期时间转换为时间戳")
async def ts_to_timestamp_api(req: DateRequest) -> TimestampResponse:
    """POST 接口：把日期文本解析为时间戳；无时区信息时按本地时区理解，非法格式返回 400。"""
    try:
        dt = parse_date_text(req.date_text)
    except ValueError:
        raise HTTPException(status_code=400, detail="无法识别的日期格式，示例：2026-10-04 12:30:00")
    local = dt.astimezone()
    # astimezone() 不带参数是"转到本地时区"，转 UTC 必须显式传入 timezone.utc
    dt_utc = local.astimezone(timezone.utc)
    seconds = int(local.timestamp())
    return TimestampResponse(
        date_text=req.date_text,
        datetime_local=local.strftime("%Y-%m-%d %H:%M:%S"),
        timestamp_seconds=seconds,
        timestamp_milliseconds=seconds * 1000,
        iso_utc=dt_utc.isoformat(),
    )
