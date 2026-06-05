from tortoise import Tortoise

# 数据库配置
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "stock_platform"

DB_URL = f"mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


async def init_db():
    """初始化 Tortoise ORM 数据库连接"""
    await Tortoise.init(
        db_url=DB_URL,
        modules={"models": ["models"]},
        use_tz=False,
        timezone="Asia/Shanghai"
    )
    await Tortoise.generate_schemas()


async def close_db():
    """关闭数据库连接"""
    await Tortoise.close_connections()


def get_db():
    """Tortoise ORM 不需要同步 get_db，异步上下文由路由处理"""
    pass