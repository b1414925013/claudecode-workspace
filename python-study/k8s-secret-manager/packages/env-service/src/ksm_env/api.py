from fastapi import APIRouter, Depends
from ksm_core.response import success_response, paginated_response
from ksm_core.pagination import Paginator
from ksm_core.security import get_current_user, require_admin
from ksm_core.exceptions import NotFoundException
from ksm_core.models import Environment
from ksm_env import schemas, services

router = APIRouter()


@router.get("/environments")
async def list_environments(page: int = 1, size: int = 20, _=Depends(get_current_user)):
    qs = Environment.filter(is_deleted=False).order_by("sort_order")
    paginator = Paginator(qs, page, size)
    result = await paginator.execute()
    items = [{
        "id": e.id, "name": e.name, "label": e.label,
        "cluster_api": e.cluster_api,
        "namespace_config": e.namespace_config,
        "k8s_sdk_mode": e.k8s_sdk_mode,
        "sort_order": e.sort_order,
        "created_at": e.created_at.isoformat(),
    } for e in result["items"]]
    return paginated_response(items=items, total=result["total"],
                              page=result["page"], size=result["size"])


@router.post("/environments")
async def create_env(data: schemas.EnvCreate, _=Depends(require_admin)):
    env = await services.create_env(data.model_dump())
    return success_response(data={"id": env.id, "name": env.name, "label": env.label})


@router.get("/environments/{env_id}")
async def get_environment(env_id: int, _=Depends(get_current_user)):
    env = await Environment.get_or_none(id=env_id, is_deleted=False)
    if not env:
        raise NotFoundException("环境不存在")
    return success_response(data={
        "id": env.id, "name": env.name, "label": env.label,
        "cluster_api": env.cluster_api,
        "namespace_config": env.namespace_config,
        "k8s_sdk_mode": env.k8s_sdk_mode,
        "sort_order": env.sort_order,
        "created_at": env.created_at.isoformat(),
    })


@router.put("/environments/{env_id}")
async def update_environment(env_id: int, data: schemas.EnvUpdate, _=Depends(require_admin)):
    env = await services.update_env(env_id, data.model_dump(exclude_unset=True))
    return success_response(data={"id": env.id, "name": env.name, "label": env.label})


@router.delete("/environments/{env_id}")
async def delete_environment(env_id: int, _=Depends(require_admin)):
    await services.delete_env(env_id)
    return success_response(message="环境已删除")


@router.get("/environments/{env_id}/namespaces")
async def get_namespaces(env_id: int, _=Depends(get_current_user)):
    namespaces = await services.get_namespaces(env_id)
    return success_response(data={"namespaces": namespaces})


@router.get("/environments/{env_id}/health")
async def check_health(env_id: int, _=Depends(get_current_user)):
    health = await services.check_health(env_id)
    return success_response(data=health)
