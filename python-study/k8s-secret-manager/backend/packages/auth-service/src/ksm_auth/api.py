from fastapi import APIRouter, Depends
from ksm_core.response import success_response, paginated_response
from ksm_core.pagination import Paginator
from ksm_core.security import get_current_user, require_admin
from ksm_core.exceptions import UnauthorizedException, NotFoundException
from ksm_core.models import User
from ksm_auth import schemas, services

router = APIRouter()


@router.post("/login")
async def login(req: schemas.LoginRequest):
    result = await services.authenticate(req.username, req.password)
    return success_response(data=result)


@router.get("/profile")
async def profile(current_user: dict = Depends(get_current_user)):
    user = await User.get_or_none(id=int(current_user["sub"]))
    if not user:
        raise UnauthorizedException("用户不存在")
    return success_response(data={
        "id": user.id, "username": user.username, "nickname": user.nickname,
        "email": user.email, "role": user.role, "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
    })


@router.get("/users")
async def list_users(page: int = 1, size: int = 20, keyword: str = "", _=Depends(require_admin)):
    qs = User.filter(is_deleted=False)
    if keyword:
        qs = qs.filter(username__icontains=keyword)
    paginator = Paginator(qs, page, size)
    result = await paginator.execute()
    items = [{
        "id": u.id, "username": u.username, "nickname": u.nickname,
        "email": u.email, "role": u.role, "is_active": u.is_active,
        "created_at": u.created_at.isoformat(),
    } for u in result["items"]]
    return paginated_response(items=items, total=result["total"],
                              page=result["page"], size=result["size"])


@router.post("/users")
async def create_user(data: schemas.UserCreate, _=Depends(require_admin)):
    user = await services.create_user(data.model_dump())
    return success_response(data={"id": user.id, "username": user.username, "role": user.role})


@router.get("/users/{user_id}")
async def get_user(user_id: int, _=Depends(require_admin)):
    user = await User.get_or_none(id=user_id, is_deleted=False)
    if not user:
        raise NotFoundException("用户不存在")
    return success_response(data={
        "id": user.id, "username": user.username, "nickname": user.nickname,
        "email": user.email, "phone": user.phone, "role": user.role,
        "is_active": user.is_active, "created_at": user.created_at.isoformat(),
    })


@router.put("/users/{user_id}")
async def update_user(user_id: int, data: schemas.UserUpdate, _=Depends(require_admin)):
    user = await services.update_user(user_id, data.model_dump(exclude_unset=True))
    return success_response(data={"id": user.id, "username": user.username, "role": user.role})


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, _=Depends(require_admin)):
    await services.delete_user(user_id)
    return success_response(message="用户已删除")


@router.put("/users/{user_id}/reset-password")
async def reset_password(user_id: int, data: schemas.ResetPassword, _=Depends(require_admin)):
    await services.reset_password(user_id, data.new_password)
    return success_response(message="密码已重置")


@router.get("/users/{user_id}/env-permissions")
async def get_env_permissions(user_id: int, _=Depends(require_admin)):
    env_ids = await services.get_env_permissions(user_id)
    return success_response(data={"env_ids": env_ids})


@router.put("/users/{user_id}/env-permissions")
async def set_env_permissions(user_id: int, data: schemas.EnvPermissionUpdate, _=Depends(require_admin)):
    await services.set_env_permissions(user_id, data.env_ids)
    return success_response(message="权限已更新")
