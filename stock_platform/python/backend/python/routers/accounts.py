from fastapi import APIRouter, Depends
from typing import Optional

from schemas import AccountCreate, AccountResponse, PaginatedResponse, PageMeta
from services import account_service
from core.pagination import pagination_params, PaginationParams
from core.errors import NotFoundError

router = APIRouter(prefix="/api/accounts", tags=["账号管理"])


@router.post("", response_model=AccountResponse)
async def create_account(account: AccountCreate):
    return await account_service.create_account(account)


@router.get("", response_model=PaginatedResponse[AccountResponse])
async def list_accounts(pagination: PaginationParams = Depends(pagination_params)):
    accounts = await account_service.list_accounts()
    total = len(accounts)

    start = (pagination.page - 1) * pagination.per_page
    end = start + pagination.per_page
    paginated_items = accounts[start:end]

    meta = PageMeta(
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=(total + pagination.per_page - 1) // pagination.per_page,
        has_next=pagination.page * pagination.per_page < total,
        has_prev=pagination.page > 1,
    )

    return PaginatedResponse(items=paginated_items, meta=meta)


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(account_id: int):
    account = await account_service.get_account(account_id)
    if not account:
        raise NotFoundError("账号不存在")
    return account


@router.delete("/{account_id}")
async def delete_account(account_id: int):
    success = await account_service.delete_account(account_id)
    if not success:
        raise NotFoundError("账号不存在")
    return {"message": "删除成功"}