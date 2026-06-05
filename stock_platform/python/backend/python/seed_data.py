from datetime import datetime, timedelta
from database import SessionLocal, init_db
from models import Account, Position, Trade, Dividend

init_db()
db = SessionLocal()

# 清空现有数据
db.query(Dividend).delete()
db.query(Trade).delete()
db.query(Position).delete()
db.query(Account).delete()
db.commit()

# 创建账号
accounts = [
    Account(name="主账户", account_type="cash"),
    Account(name="融资账户", account_type="margin"),
]
db.add_all(accounts)
db.commit()

# 创建持仓
positions = [
    Position(account_id=1, stock_code="600519", stock_name="贵州茅台", quantity=100, avg_cost=1800.0),
    Position(account_id=1, stock_code="000858", stock_name="五粮液", quantity=500, avg_cost=150.0),
    Position(account_id=2, stock_code="600036", stock_name="招商银行", quantity=1000, avg_cost=35.0),
]
db.add_all(positions)
db.commit()

# 创建交易记录
today = datetime.now()
trades = [
    # 主账户 - 贵州茅台
    Trade(account_id=1, stock_code="600519", stock_name="贵州茅台", trade_type="buy",
          quantity=100, price=1800.0, commission=5.0, trade_date=today - timedelta(days=60)),
    # 主账户 - 五粮液
    Trade(account_id=1, stock_code="000858", stock_name="五粮液", trade_type="buy",
          quantity=300, price=145.0, commission=3.0, trade_date=today - timedelta(days=45)),
    Trade(account_id=1, stock_code="000858", stock_name="五粮液", trade_type="buy",
          quantity=200, price=155.0, commission=3.0, trade_date=today - timedelta(days=30)),
    # 主账户 - 卖出五粮液（部分）
    Trade(account_id=1, stock_code="000858", stock_name="五粮液", trade_type="sell",
          quantity=200, price=165.0, commission=3.0, trade_date=today - timedelta(days=15)),
    # 融资账户 - 招商银行
    Trade(account_id=2, stock_code="600036", stock_name="招商银行", trade_type="buy",
          quantity=1000, price=35.0, commission=5.0, trade_date=today - timedelta(days=20)),
]
db.add_all(trades)
db.commit()

# 创建分红记录
dividends = [
    Dividend(account_id=1, stock_code="600519", stock_name="贵州茅台", dividend_amount=2000.0,
             dividend_date=today - timedelta(days=90)),
    Dividend(account_id=1, stock_code="000858", stock_name="五粮液", dividend_amount=1500.0,
             dividend_date=today - timedelta(days=60)),
    Dividend(account_id=2, stock_code="600036", stock_name="招商银行", dividend_amount=800.0,
             dividend_date=today - timedelta(days=30)),
]
db.add_all(dividends)
db.commit()

db.close()
print("测试数据已添加完成！")