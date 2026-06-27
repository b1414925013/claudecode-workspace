from ksm_core.models import Environment
from ksm_core.exceptions import NotFoundException, BadRequestException
from ksm_core.k8s_client import K8sClient


async def create_env(data: dict) -> Environment:
    existing = await Environment.get_or_none(name=data["name"])
    if existing:
        raise BadRequestException("环境名称已存在")
    return await Environment.create(**data)


async def update_env(env_id: int, data: dict) -> Environment:
    env = await Environment.get_or_none(id=env_id, is_deleted=False)
    if not env:
        raise NotFoundException("环境不存在")
    await env.update_from_dict(data)
    await env.save()
    return env


async def delete_env(env_id: int):
    env = await Environment.get_or_none(id=env_id, is_deleted=False)
    if not env:
        raise NotFoundException("环境不存在")
    env.is_deleted = True
    await env.save()


async def get_namespaces(env_id: int) -> list[dict]:
    env = await Environment.get_or_none(id=env_id, is_deleted=False)
    if not env:
        raise NotFoundException("环境不存在")
    client = K8sClient(env)
    return await client.get_namespaces()


async def check_health(env_id: int) -> dict:
    env = await Environment.get_or_none(id=env_id, is_deleted=False)
    if not env:
        raise NotFoundException("环境不存在")
    client = K8sClient(env)
    return await client.check_health()
