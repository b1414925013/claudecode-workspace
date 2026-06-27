from datetime import datetime, timedelta, timezone
from ksm_core.models import Environment, SecretCache, DBCredential, AuditLog
from ksm_core.config import settings
from ksm_core.exceptions import NotFoundException
from ksm_core.k8s_client import K8sClient
from ksm_core.crypto_utils import aes_encrypt, aes_decrypt
from ksm_core.pagination import Paginator


async def list_secrets(env_id: int, namespace: str) -> list[dict]:
    env = await Environment.get_or_none(id=env_id, is_deleted=False)
    if not env:
        raise NotFoundException("环境不存在")
    client = K8sClient(env)
    return await client.list_secrets(namespace)


async def get_secret_value(env_id: int, namespace: str, secret_name: str, key: str) -> str:
    env = await Environment.get_or_none(id=env_id, is_deleted=False)
    if not env:
        raise NotFoundException("环境不存在")
    client = K8sClient(env)
    return await client.get_secret_value(namespace, secret_name, key)


async def sync_secret_cache(env_id: int, namespace: str):
    env = await Environment.get_or_none(id=env_id, is_deleted=False)
    if not env:
        raise NotFoundException("环境不存在")
    client = K8sClient(env)
    secrets = await client.list_secrets(namespace)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.SECRET_CACHE_TTL)
    for s in secrets:
        raw_data = {}
        for k in s["keys"]:
            try:
                raw_data[k] = await client.get_secret_value(namespace, s["name"], k)
            except Exception:
                raw_data[k] = ""
        await SecretCache.update_or_create(
            env_id=env_id, namespace=namespace, secret_name=s["name"],
            defaults={
                "secret_type": s["type"],
                "data_keys": s["keys"],
                "data_snapshot": str(raw_data),
                "fetched_at": datetime.now(timezone.utc),
                "expires_at": expires_at,
            },
        )


async def list_credentials(env_id: int = None, db_type: str = None,
                           service_name: str = None, page: int = 1, size: int = 20) -> dict:
    qs = DBCredential.filter(is_deleted=False)
    if env_id:
        qs = qs.filter(env_id=env_id)
    if db_type:
        qs = qs.filter(db_type=db_type)
    if service_name:
        qs = qs.filter(service_name__icontains=service_name)
    paginator = Paginator(qs, page, size)
    result = await paginator.execute()
    items = []
    for c in result["items"]:
        items.append({
            "id": c.id, "env_id": c.env_id, "service_name": c.service_name,
            "db_type": c.db_type, "host": c.host, "port": c.port,
            "database_name": c.database_name, "username": c.username,
            "password_masked": "******",
            "description": c.description,
            "created_at": c.created_at.isoformat(),
        })
    return {"items": items, **{k: result[k] for k in ("total", "page", "size", "pages")}}


async def create_credential(data: dict) -> DBCredential:
    data["password_encrypted"] = aes_encrypt(data.pop("password"))
    return await DBCredential.create(**data)


async def update_credential(cred_id: int, data: dict) -> DBCredential:
    cred = await DBCredential.get_or_none(id=cred_id, is_deleted=False)
    if not cred:
        raise NotFoundException("凭据不存在")
    if "password" in data and data["password"]:
        data["password_encrypted"] = aes_encrypt(data.pop("password"))
    else:
        data.pop("password", None)
    await cred.update_from_dict(data)
    await cred.save()
    return cred


async def delete_credential(cred_id: int):
    cred = await DBCredential.get_or_none(id=cred_id, is_deleted=False)
    if not cred:
        raise NotFoundException("凭据不存在")
    cred.is_deleted = True
    await cred.save()


async def reveal_credential(cred_id: int, current_user: dict, ip: str = "", ua: str = "") -> str:
    cred = await DBCredential.get_or_none(id=cred_id, is_deleted=False)
    if not cred:
        raise NotFoundException("凭据不存在")
    password = aes_decrypt(cred.password_encrypted)
    await AuditLog.create(
        user_id=int(current_user["sub"]),
        username=current_user["username"],
        action="view_credential_password",
        resource_type="db_credential",
        resource_id=str(cred_id),
        resource_name=f"{cred.service_name}/{cred.db_type}",
        detail={"env_id": cred.env_id, "host": cred.host, "username": cred.username},
        ip_address=ip,
        user_agent=ua,
        status="success",
    )
    return password
