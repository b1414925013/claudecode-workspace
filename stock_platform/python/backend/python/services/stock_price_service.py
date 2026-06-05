import requests
import time
from models import StockPrice, Position
from datetime import datetime, timedelta
from typing import Optional


def get_eastmoney_code(stock_code: str) -> str:
    if stock_code.startswith("6"):
        return f"1.{stock_code}"
    elif stock_code.startswith(("0", "3")):
        return f"0.{stock_code}"
    return stock_code


def fetch_stock_price(stock_code: str, retries: int = 3) -> Optional[dict]:
    for i in range(retries):
        try:
            em_code = get_eastmoney_code(stock_code)
            url = f"https://push2.eastmoney.com/api/qt/stock/get"

            params = {
                "secid": em_code,
                "fields": "f43,f44,f57,f58"
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if data.get("data") and data["data"].get("f43"):
                price = float(data["data"]["f43"]) / 100
                prev_close = float(data["data"]["f44"]) / 100 if data["data"].get("f44") else price
                change_value = price - prev_close
                change_percent = change_value / prev_close * 100 if prev_close else 0

                return {
                    "price": price,
                    "change_value": change_value,
                    "change_percent": change_percent,
                    "trade_date": datetime.now()
                }
            else:
                print(f"股票 {stock_code} 数据格式异常: {data}")
                return None

        except Exception as e:
            print(f"获取股票 {stock_code} 价格失败 (尝试 {i+1}/{retries}): {e}")
            if i < retries - 1:
                time.sleep(1)
    return None


async def fetch_and_save_price(stock_code: str) -> Optional[StockPrice]:
    data = fetch_stock_price(stock_code)
    if not data or data["price"] is None:
        return None

    return await StockPrice.create(
        stock_code=stock_code,
        price=data["price"],
        change_value=data.get("change_value"),
        change_percent=data["change_percent"],
        trade_date=data["trade_date"]
    )


async def update_all_positions_price() -> int:
    positions = await Position.all()
    stock_codes = set(pos.stock_code for pos in positions)

    count = 0
    for code in stock_codes:
        result = await fetch_and_save_price(code)
        if result:
            count += 1
        time.sleep(0.5)

    return count


async def get_latest_price(stock_code: str) -> Optional[StockPrice]:
    price = await StockPrice.filter(stock_code=stock_code).order_by("-trade_date").first()
    return price


async def get_price_history(stock_code: str, days: int = 30) -> list[StockPrice]:
    start_date = datetime.now() - timedelta(days=days)
    return await StockPrice.filter(
        stock_code=stock_code,
        trade_date__gte=start_date
    ).order_by("trade_date")