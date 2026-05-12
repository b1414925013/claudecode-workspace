from models import Position
from schemas import PositionCreate
from datetime import datetime
from tortoise.exceptions import DoesNotExist


async def create_position(position: PositionCreate) -> Position:
    return await Position.create(
        account_id=position.account_id,
        stock_code=position.stock_code,
        stock_name=position.stock_name,
        quantity=position.quantity,
        avg_cost=position.avg_cost
    )


async def list_positions(account_id: int | None = None) -> list[Position]:
    query = Position.all()
    if account_id:
        query = query.filter(account_id=account_id)
    return await query


async def list_positions_by_account(account_id: int) -> list[Position]:
    return await Position.filter(account_id=account_id).all()


async def get_position(position_id: int) -> Position | None:
    try:
        return await Position.get(id=position_id)
    except DoesNotExist:
        return None


async def update_position(position_id: int, position_data: PositionCreate) -> Position | None:
    position = await get_position(position_id)
    if not position:
        return None

    total_quantity = position.quantity + position_data.quantity
    if total_quantity > 0:
        total_cost = position.quantity * position.avg_cost + position_data.quantity * position_data.avg_cost
        position.avg_cost = total_cost / total_quantity
    position.quantity = total_quantity
    position.updated_at = datetime.now()

    await position.save()
    return position


async def delete_position(position_id: int) -> bool:
    position = await get_position(position_id)
    if not position:
        return False
    await position.delete()
    return True