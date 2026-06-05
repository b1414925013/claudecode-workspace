from models import Trade, Position
from schemas import TradeCreate
from datetime import datetime
from typing import Optional


async def create_trade(trade: TradeCreate) -> Trade:
    db_trade = await Trade.create(
        account_id=trade.account_id,
        stock_code=trade.stock_code,
        stock_name=trade.stock_name,
        trade_type=trade.trade_type,
        quantity=trade.quantity,
        price=trade.price,
        commission=trade.commission,
        trade_date=trade.trade_date
    )

    position = await Position.filter(
        account_id=trade.account_id,
        stock_code=trade.stock_code
    ).first()

    if trade.trade_type == "buy":
        if position:
            total_quantity = position.quantity + trade.quantity
            total_cost = position.quantity * position.avg_cost + trade.quantity * trade.price
            position.avg_cost = total_cost / total_quantity
            position.quantity = total_quantity
            position.updated_at = datetime.now()
            await position.save()
        else:
            await Position.create(
                account_id=trade.account_id,
                stock_code=trade.stock_code,
                stock_name=trade.stock_name,
                quantity=trade.quantity,
                avg_cost=trade.price
            )
    elif trade.trade_type == "sell":
        if position:
            profit = (trade.price - position.avg_cost) * trade.quantity - trade.commission
            db_trade.profit = profit
            await db_trade.save()
            position.quantity -= trade.quantity
            position.updated_at = datetime.now()
            if position.quantity <= 0:
                await position.delete()
            else:
                await position.save()

    return db_trade


async def list_trades(
    account_id: int | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None
) -> list[Trade]:
    query = Trade.all()
    if account_id is not None:
        query = query.filter(account_id=account_id)
    if start_date:
        query = query.filter(trade_date__gte=start_date)
    if end_date:
        query = query.filter(trade_date__lte=end_date)
    return await query.order_by("-trade_date")