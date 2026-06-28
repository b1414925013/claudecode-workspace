import json
import tempfile
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from ksm_core.response import success_response, paginated_response
from ksm_core.security import get_current_user, require_admin
from ksm_core.exceptions import NotFoundException
from ksm_core.models import DBCredential, AuditLog
from ksm_core.crypto_utils import aes_decrypt
from ksm_secret import schemas, services

router = APIRouter()


@router.get("/secrets/list")
async def list_secrets(env_id: int = Query(...), namespace: str = Query(...),
                       _=Depends(get_current_user)):
    secrets = await services.list_secrets(env_id, namespace)
    return success_response(data={"secrets": secrets})


@router.get("/secrets/detail")
async def get_secret_detail(
    env_id: int = Query(...), namespace: str = Query(...),
    secret_name: str = Query(...), key: str = Query(...),
    _=Depends(get_current_user),
):
    value = await services.get_secret_value(env_id, namespace, secret_name, key)
    return success_response(data={"value": value, "key": key})


@router.post("/secrets/sync")
async def sync_secrets(data: schemas.SyncRequest, _=Depends(get_current_user)):
    await services.sync_secret_cache(data.env_id, data.namespace)
    return success_response(message="同步完成")


@router.get("/credentials")
async def list_credentials(
    env_id: Optional[int] = Query(None), db_type: Optional[str] = Query(None),
    service_name: Optional[str] = Query(None), page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100), _=Depends(get_current_user),
):
    result = await services.list_credentials(env_id, db_type, service_name, page, size)
    return paginated_response(items=result["items"], total=result["total"],
                              page=result["page"], size=result["size"])


@router.post("/credentials")
async def create_credential(data: schemas.CredentialCreate,
                            current_user: dict = Depends(get_current_user)):
    cred = await services.create_credential(data.model_dump())
    await AuditLog.create(
        user_id=int(current_user["sub"]), username=current_user["username"],
        action="create_credential", resource_type="db_credential",
        resource_id=str(cred.id), resource_name=cred.service_name,
        status="success",
    )
    return success_response(data={"id": cred.id, "service_name": cred.service_name})


@router.get("/credentials/{cred_id}")
async def get_credential(cred_id: int, _=Depends(get_current_user)):
    cred = await DBCredential.get_or_none(id=cred_id, is_deleted=False)
    if not cred:
        raise NotFoundException("凭据不存在")
    return success_response(data={
        "id": cred.id, "env_id": cred.env_id, "service_name": cred.service_name,
        "db_type": cred.db_type, "host": cred.host, "port": cred.port,
        "database_name": cred.database_name, "username": cred.username,
        "password_masked": "******", "description": cred.description,
        "created_at": cred.created_at.isoformat(),
    })


@router.put("/credentials/{cred_id}")
async def update_credential(cred_id: int, data: schemas.CredentialUpdate,
                            _=Depends(require_admin)):
    cred = await services.update_credential(cred_id, data.model_dump(exclude_unset=True))
    return success_response(data={"id": cred.id, "service_name": cred.service_name})


@router.delete("/credentials/{cred_id}")
async def delete_credential(cred_id: int, _=Depends(require_admin)):
    await services.delete_credential(cred_id)
    return success_response(message="凭据已删除")


@router.post("/credentials/{cred_id}/reveal")
async def reveal_credential(cred_id: int, request: Request,
                            current_user: dict = Depends(get_current_user)):
    password = await services.reveal_credential(
        cred_id, current_user,
        ip=request.client.host if request.client else "",
        ua=request.headers.get("User-Agent", ""),
    )
    return success_response(data={"password": password})


@router.post("/credentials/export")
async def export_credentials(env_id: int = Query(...),
                              db_type: Optional[str] = Query(None),
                              _=Depends(require_admin)):
    qs = DBCredential.filter(is_deleted=False, env_id=env_id)
    if db_type:
        qs = qs.filter(db_type=db_type)
    creds = await qs
    export_data = []
    for c in creds:
        export_data.append({
            "service_name": c.service_name, "db_type": c.db_type,
            "host": c.host, "port": c.port, "database": c.database_name,
            "username": c.username,
            "password": aes_decrypt(c.password_encrypted),
        })
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", prefix="credential_export_", delete=False,
    )
    json.dump(export_data, tmp, indent=2, ensure_ascii=False)
    tmp.close()
    return success_response(data={"file_path": tmp.name, "count": len(export_data)})
