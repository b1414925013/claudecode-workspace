from ksm_core.models import User, EnvPermission
from ksm_core.security import hash_password, verify_password, create_access_token
from ksm_core.exceptions import BadRequestException, UnauthorizedException, NotFoundException


async def authenticate(username: str, password: str) -> dict:
    user = await User.get_or_none(username=username, is_deleted=False)
    if not user or not user.is_active:
        raise UnauthorizedException("用户名或密码错误")
    if not verify_password(password, user.password_hash):
        raise UnauthorizedException("用户名或密码错误")
    token = create_access_token(user.id, user.username, user.role)
    return {
        "token": token,
        "user_id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "role": user.role,
    }


async def create_user(data: dict) -> User:
    existing = await User.get_or_none(username=data["username"])
    if existing:
        raise BadRequestException("用户名已存在")
    data["password_hash"] = hash_password(data.pop("password"))
    return await User.create(**data)


async def update_user(user_id: int, data: dict) -> User:
    user = await User.get_or_none(id=user_id, is_deleted=False)
    if not user:
        raise NotFoundException("用户不存在")
    await user.update_from_dict(data)
    await user.save()
    return user


async def delete_user(user_id: int):
    user = await User.get_or_none(id=user_id, is_deleted=False)
    if not user:
        raise NotFoundException("用户不存在")
    user.is_deleted = True
    await user.save()


async def reset_password(user_id: int, new_password: str):
    user = await User.get_or_none(id=user_id, is_deleted=False)
    if not user:
        raise NotFoundException("用户不存在")
    user.password_hash = hash_password(new_password)
    await user.save()


async def set_env_permissions(user_id: int, env_ids: list[int]):
    await EnvPermission.filter(user_id=user_id).delete()
    permissions = [EnvPermission(user_id=user_id, env_id=eid) for eid in env_ids]
    await EnvPermission.bulk_create(permissions)


async def get_env_permissions(user_id: int) -> list[int]:
    perms = await EnvPermission.filter(user_id=user_id)
    return [p.env_id for p in perms]
