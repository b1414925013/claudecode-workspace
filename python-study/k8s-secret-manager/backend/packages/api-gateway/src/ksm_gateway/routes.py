import csv
import io
from typing import Optional
from fastapi import APIRouter, Depends, Query
from ksm_core.response import success_response, paginated_response
from ksm_core.security import require_admin, get_current_user
from ksm_core.pagination import Paginator
from ksm_core.models import AuditLog, User, Environment, SecretCache, DBCredential

router = APIRouter()


@router.get("/audit-logs")
async def list_audit_logs(
    action: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    resource_type: Optional[str] = Query(None),
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _=Depends(require_admin),
):
    qs = AuditLog.all().order_by("-created_at")
    if action:
        qs = qs.filter(action=action)
    if user_id:
        qs = qs.filter(user_id=user_id)
    if resource_type:
        qs = qs.filter(resource_type=resource_type)
    paginator = Paginator(qs, page, size)
    result = await paginator.execute()
    items = [{
        "id": log.id, "user_id": log.user_id, "username": log.username,
        "action": log.action, "resource_type": log.resource_type,
        "resource_id": log.resource_id, "resource_name": log.resource_name,
        "detail": log.detail, "ip_address": log.ip_address,
        "status": log.status, "created_at": log.created_at.isoformat(),
    } for log in result["items"]]
    return paginated_response(items=items, total=result["total"],
                              page=result["page"], size=result["size"])


@router.get("/audit-logs/export")
async def export_audit_logs(
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
    _=Depends(require_admin),
):
    qs = AuditLog.all().order_by("-created_at")
    logs = await qs
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "username", "action", "resource_type",
                     "resource_id", "resource_name", "ip", "status", "created_at"])
    for log in logs:
        writer.writerow([
            log.id, log.username, log.action, log.resource_type,
            log.resource_id, log.resource_name, log.ip_address,
            log.status, log.created_at.isoformat(),
        ])
    from fastapi.responses import StreamingResponse
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_logs.csv"},
    )


@router.get("/dashboard/stats")
async def dashboard_stats(_=Depends(get_current_user)):
    env_count = await Environment.filter(is_deleted=False).count()
    secret_count = await SecretCache.all().count()
    user_count = await User.filter(is_deleted=False, is_active=True).count()
    cred_count = await DBCredential.filter(is_deleted=False).count()
    recent_logs = await AuditLog.all().order_by("-created_at").limit(10)
    return success_response(data={
        "env_count": env_count,
        "secret_count": secret_count,
        "user_count": user_count,
        "credential_count": cred_count,
        "recent_logs": [{
            "id": l.id, "username": l.username, "action": l.action,
            "resource_type": l.resource_type,
            "created_at": l.created_at.isoformat(),
        } for l in recent_logs],
    })
