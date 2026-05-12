from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime

from schemas import TradeCreate, TradeResponse, PaginatedResponse, PageMeta
from services import trade_service
from core.pagination import pagination_params, PaginationParams

router = APIRouter(prefix="/api/trades", tags=["交易记录"])


@router.post("", response_model=TradeResponse)
async def create_trade(trade: TradeCreate):
    return await trade_service.create_trade(trade)


@router.get("", response_model=PaginatedResponse[TradeResponse])
async def list_trades(
    account_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    pagination: PaginationParams = Depends(pagination_params)
):
    trades = await trade_service.list_trades(account_id, start_date, end_date)
    total = len(trades)

    start = (pagination.page - 1) * pagination.per_page
    end = start + pagination.per_page
    paginated_items = trades[start:end]

    meta = PageMeta(
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=(total + pagination.per_page - 1) // pagination.per_page if total > 0 else 0,
        has_next=pagination.page * pagination.per_page < total,
        has_prev=pagination.page > 1,
    )

    return PaginatedResponse(items=paginated_items, meta=meta)