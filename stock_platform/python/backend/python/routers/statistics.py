from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime

from schemas import StatisticsResponse, SummaryResponse
from services import statistics_service

router = APIRouter(prefix="/api", tags=["统计分析"])


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(
    account_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    return await statistics_service.get_statistics(account_id, start_date, end_date)


@router.get("/summary", response_model=SummaryResponse)
async def get_summary():
    return await statistics_service.get_summary()