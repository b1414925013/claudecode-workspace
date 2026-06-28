from tortoise import Tortoise
from ksm_core.config import settings


async def init_db():
    await Tortoise.init(
        db_url=settings.db_url,
        modules={"models": ["ksm_core.models"]},
    )


async def close_db():
    await Tortoise.close_connections()
