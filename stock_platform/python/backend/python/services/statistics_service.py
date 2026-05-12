from models import Trade, Account, Position
from schemas import StatisticsResponse, SummaryResponse
from typing import Optional
from datetime import datetime
from services import stock_price_service


async def get_statistics(
    account_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> StatisticsResponse:
    # 从持仓计算
    position_query = Position.all()
    if account_id is not None:
        position_query = position_query.filter(account_id=account_id)
    positions = await position_query

    # 计算持仓成本
    total_cost = sum([pos.quantity * pos.avg_cost for pos in positions])

    # 计算当前市值
    total_market_value = 0
    for pos in positions:
        price_data = await stock_price_service.get_latest_price(pos.stock_code)
        if price_data:
            total_market_value += pos.quantity * price_data.price

    total_profit = total_market_value - total_cost
    return_rate = total_profit / total_cost if total_cost > 0 else 0

    # 从交易记录计算
    trade_query = Trade.all()
    if account_id is not None:
        trade_query = trade_query.filter(account_id=account_id)
    if start_date:
        trade_query = trade_query.filter(trade_date__gte=start_date)
    if end_date:
        trade_query = trade_query.filter(trade_date__lte=end_date)

    trades = await trade_query
    winning_trades = len([t for t in trades if t.profit and t.profit > 0])
    total_trades = len([t for t in trades if t.trade_type == "sell"])
    win_rate = winning_trades / total_trades if total_trades > 0 else 0

    return StatisticsResponse(
        total_profit=total_profit,
        total_cost=total_cost,
        total_market_value=total_market_value,
        return_rate=return_rate,
        win_rate=win_rate,
        total_trades=total_trades,
        winning_trades=winning_trades,
        losing_trades=total_trades - winning_trades,
        avg_holding_days=0
    )


async def get_summary() -> SummaryResponse:
    accounts = await Account.all()
    positions = await Position.all()
    trades = await Trade.all()

    total_cost = sum([pos.quantity * pos.avg_cost for pos in positions])

    total_market_value = 0
    for pos in positions:
        price_data = await stock_price_service.get_latest_price(pos.stock_code)
        if price_data:
            total_market_value += pos.quantity * price_data.price

    total_profit = total_market_value - total_cost

    return SummaryResponse(
        total_accounts=len(accounts),
        total_positions=len(positions),
        total_trades=len(trades),
        total_cost=total_cost,
        total_profit=total_profit
    )