from fastapi import APIRouter, Depends, Query, HTTPException

from schemas import StockPriceResponse, StockPriceHistoryResponse
from services import stock_price_service

router = APIRouter(prefix="/api/stock-prices", tags=["股票价格"])


@router.post("/sync", response_model=dict)
async def sync_all_prices():
    """同步所有持仓股票价格"""
    count = await stock_price_service.update_all_positions_price()
    return {"message": f"成功更新 {count} 只股票价格"}


@router.post("/{stock_code}", response_model=StockPriceResponse)
async def sync_single_price(stock_code: str):
    """同步单只股票价格"""
    result = await stock_price_service.fetch_and_save_price(stock_code)
    if not result:
        raise HTTPException(status_code=500, detail="获取价格失败")
    return result


@router.get("/{stock_code}/latest", response_model=StockPriceResponse)
async def get_latest_price(stock_code: str):
    """获取股票最新价格"""
    price = await stock_price_service.get_latest_price(stock_code)
    if not price:
        raise HTTPException(status_code=404, detail="暂无价格数据")
    return price


@router.get("/{stock_code}/history", response_model=StockPriceHistoryResponse)
async def get_price_history(stock_code: str, days: int = Query(30, ge=1, le=365)):
    """获取股票历史价格"""
    prices = await stock_price_service.get_price_history(stock_code, days)
    return StockPriceHistoryResponse(stock_code=stock_code, prices=prices)