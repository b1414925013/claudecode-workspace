from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from schemas import PositionCreate, PositionResponse, PaginatedResponse, PageMeta
from services import position_service, stock_price_service
from core.pagination import pagination_params, PaginationParams
from core.errors import NotFoundError

router = APIRouter(prefix="/api/positions", tags=["持仓管理"])


@router.post("", response_model=PositionResponse)
async def create_position(position: PositionCreate):
    return await position_service.create_position(position)


@router.get("", response_model=PaginatedResponse[PositionResponse])
async def list_positions(
    account_id: Optional[int] = Query(None),
    pagination: PaginationParams = Depends(pagination_params)
):
    positions = await position_service.list_positions(account_id)
    total = len(positions)

    start = (pagination.page - 1) * pagination.per_page
    end = start + pagination.per_page
    paginated_positions = positions[start:end]

    result = []
    for pos in paginated_positions:
        price_data = await stock_price_service.get_latest_price(pos.stock_code)
        pos_dict = {
            "id": pos.id,
            "account_id": pos.account_id,
            "stock_code": pos.stock_code,
            "stock_name": pos.stock_name,
            "quantity": pos.quantity,
            "avg_cost": pos.avg_cost,
            "created_at": pos.created_at,
            "updated_at": pos.updated_at,
        }
        if price_data:
            pos_dict["current_price"] = price_data.price
            pos_dict["change_value"] = price_data.change_value
            pos_dict["change_percent"] = price_data.change_percent
            pos_dict["market_value"] = pos.quantity * price_data.price
        result.append(PositionResponse(**pos_dict))

    meta = PageMeta(
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=(total + pagination.per_page - 1) // pagination.per_page if total > 0 else 0,
        has_next=pagination.page * pagination.per_page < total,
        has_prev=pagination.page > 1,
    )

    return PaginatedResponse(items=result, meta=meta)


@router.get("/account/{account_id}", response_model=List[PositionResponse])
async def list_positions_by_account(account_id: int):
    positions = await position_service.list_positions_by_account(account_id)

    result = []
    for pos in positions:
        price_data = await stock_price_service.get_latest_price(pos.stock_code)
        pos_dict = {
            "id": pos.id,
            "account_id": pos.account_id,
            "stock_code": pos.stock_code,
            "stock_name": pos.stock_name,
            "quantity": pos.quantity,
            "avg_cost": pos.avg_cost,
            "created_at": pos.created_at,
            "updated_at": pos.updated_at,
        }
        if price_data:
            pos_dict["current_price"] = price_data.price
            pos_dict["change_value"] = price_data.change_value
            pos_dict["change_percent"] = price_data.change_percent
            pos_dict["market_value"] = pos.quantity * price_data.price
        result.append(PositionResponse(**pos_dict))
    return result


@router.get("/{position_id}", response_model=PositionResponse)
async def get_position(position_id: int):
    position = await position_service.get_position(position_id)
    if not position:
        raise NotFoundError("持仓不存在")
    return position


@router.put("/{position_id}", response_model=PositionResponse)
async def update_position(position_id: int, position: PositionCreate):
    result = await position_service.update_position(position_id, position)
    if not result:
        raise NotFoundError("持仓不存在")
    return result


@router.delete("/{position_id}")
async def delete_position(position_id: int):
    success = await position_service.delete_position(position_id)
    if not success:
        raise NotFoundError("持仓不存在")
    return {"message": "删除成功"}