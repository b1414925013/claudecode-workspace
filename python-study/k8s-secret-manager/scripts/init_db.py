"""Initialize database tables and create default admin user."""
import asyncio
from tortoise import Tortoise
from ksm_core.database import init_db, close_db
from ksm_core.models import User
from ksm_core.security import hash_password
from ksm_core.config import settings


async def main():
    print(f"Connecting to database: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    await init_db()
    from tortoise import Tortoise as T
    await T.generate_schemas()

    admin = await User.get_or_none(username="admin")
    if not admin:
        await User.create(
            username="admin",
            password_hash=hash_password("admin123"),
            nickname="系统管理员",
            role="admin",
            is_active=True,
        )
        print("Default admin user created: admin / admin123")
    else:
        print("Admin user already exists")

    await close_db()
    print("Database initialization complete.")


if __name__ == "__main__":
    asyncio.run(main())
