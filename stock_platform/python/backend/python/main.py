from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import uuid

from database import init_db, close_db
from middleware import RequestContextMiddleware
from routers import accounts, positions, trades, dividends, statistics, stock_prices
from services import stock_price_service
from core.errors import register_exception_handlers
from core.logging import setup_logging, log_extra

app = FastAPI(title="股票收益记录平台 API", version="1.0.0")

# 注册全局异常处理器
register_exception_handlers(app)

# 请求上下文中间件
app.add_middleware(RequestContextMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置结构化日志
logger = setup_logging(level="INFO", log_format="json", logger_name="stock_platform")


def daily_update_prices():
    """每天收盘后更新股票价格（APScheduler 回调）"""
    import asyncio
    request_id = str(uuid.uuid4())
    logger.info(
        "开始更新股票价格",
        extra=log_extra(request_id=request_id, event_type="price_update_start")
    )
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        count = loop.run_until_complete(stock_price_service.update_all_positions_price())
        logger.info(
            f"成功更新 {count} 只股票价格",
            extra=log_extra(request_id=request_id, event_type="price_update_complete", stock_count=count)
        )
    except Exception as e:
        logger.error(
            f"更新股票价格失败: {e}",
            extra=log_extra(request_id=request_id, event_type="price_update_error")
        )
    finally:
        loop.close()


scheduler = BackgroundScheduler()


@app.on_event("startup")
async def startup_event():
    await init_db()
    # 设置每天 16:00 执行一次价格更新
    scheduler.add_job(daily_update_prices, "cron", hour=16, minute=0)
    scheduler.start()


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(close_db())


# 注册路由
app.include_router(accounts.router)
app.include_router(positions.router)
app.include_router(trades.router)
app.include_router(dividends.router)
app.include_router(statistics.router)
app.include_router(stock_prices.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)