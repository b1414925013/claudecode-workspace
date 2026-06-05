from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Generic, TypeVar

T = TypeVar("T")


class PageMeta(BaseModel):
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    meta: PageMeta


class AccountCreate(BaseModel):
    name: str
    account_type: str = "cash"


class AccountResponse(BaseModel):
    id: int
    name: str
    account_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class PositionCreate(BaseModel):
    account_id: int
    stock_code: str
    stock_name: str
    quantity: int
    avg_cost: float


class PositionResponse(BaseModel):
    id: int
    account_id: int
    stock_code: str
    stock_name: str
    quantity: int
    avg_cost: float
    current_price: Optional[float] = None
    change_value: Optional[float] = None
    change_percent: Optional[float] = None
    market_value: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TradeCreate(BaseModel):
    account_id: int
    stock_code: str
    stock_name: str
    trade_type: str
    quantity: int
    price: float
    commission: float = 0.0
    trade_date: datetime


class TradeResponse(BaseModel):
    id: int
    account_id: int
    stock_code: str
    stock_name: str
    trade_type: str
    quantity: int
    price: float
    commission: float
    trade_date: datetime
    profit: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DividendCreate(BaseModel):
    account_id: int
    stock_code: str
    stock_name: str
    dividend_amount: float
    dividend_date: datetime


class DividendResponse(BaseModel):
    id: int
    account_id: int
    stock_code: str
    stock_name: str
    dividend_amount: float
    dividend_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class StatisticsResponse(BaseModel):
    total_profit: float
    total_cost: float
    total_market_value: float
    return_rate: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_holding_days: float


class SummaryResponse(BaseModel):
    total_accounts: int
    total_positions: int
    total_trades: int
    total_cost: float
    total_profit: float


class StockPriceResponse(BaseModel):
    id: int
    stock_code: str
    price: float
    change_value: Optional[float] = None
    change_percent: Optional[float] = None
    trade_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class StockPriceHistoryResponse(BaseModel):
    stock_code: str
    prices: list[StockPriceResponse]