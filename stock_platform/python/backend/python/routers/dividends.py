from fastapi import APIRouter, Depends, Query
from typing import Optional

from schemas import DividendCreate, DividendResponse, PaginatedResponse, PageMeta
from services import dividend_service
from core.pagination import pagination_params, PaginationParams

router = APIRouter(prefix="/api/dividends", tags=["分红记录"])


@router.post("", response_model=DividendResponse)
async def create_dividend(dividend: DividendCreate):
    return await dividend_service.create_dividend(dividend)


@router.get("", response_model=PaginatedResponse[DividendResponse])
async def list_dividends(
    account_id: Optional[int] = Query(None),
    pagination: PaginationParams = Depends(pagination_params)
):
    dividends = await dividend_service.list_dividends(account_id)
    total = len(dividends)

    start = (pagination.page - 1) * pagination.per_page
    end = start + pagination.per_page
    paginated_items = dividends[start:end]

    meta = PageMeta(
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=(total + pagination.per_page - 1) // pagination.per_page if total > 0 else 0,
        has_next=pagination.page * pagination.per_page < total,
        has_prev=pagination.page > 1,
    )

    return PaginatedResponse(items=paginated_items, meta=meta)