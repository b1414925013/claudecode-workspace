from models import Account
from schemas import AccountCreate
from tortoise.exceptions import DoesNotExist


async def create_account(account: AccountCreate) -> Account:
    return await Account.create(
        name=account.name,
        account_type=account.account_type
    )


async def list_accounts() -> list[Account]:
    return await Account.all().order_by("id")


async def get_account(account_id: int) -> Account | None:
    try:
        return await Account.get(id=account_id)
    except DoesNotExist:
        return None


async def delete_account(account_id: int) -> bool:
    account = await get_account(account_id)
    if not account:
        return False
    await account.delete()
    return True