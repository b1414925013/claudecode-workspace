from models import Dividend
from schemas import DividendCreate


async def create_dividend(dividend: DividendCreate) -> Dividend:
    return await Dividend.create(
        account_id=dividend.account_id,
        stock_code=dividend.stock_code,
        stock_name=dividend.stock_name,
        dividend_amount=dividend.dividend_amount,
        dividend_date=dividend.dividend_date
    )


async def list_dividends(account_id: int | None = None) -> list[Dividend]:
    query = Dividend.all()
    if account_id is not None:
        query = query.filter(account_id=account_id)
    return await query.order_by("-dividend_date")