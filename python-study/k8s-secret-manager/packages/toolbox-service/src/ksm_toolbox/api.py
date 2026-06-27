from fastapi import APIRouter, Depends, Query
from ksm_core.response import success_response
from ksm_core.security import get_current_user, require_admin
from ksm_toolbox import schemas, services

router = APIRouter()


@router.post("/tools/json-format")
async def json_format(data: schemas.JsonFormatInput, _=Depends(get_current_user)):
    result = services.json_format(data.input, data.indent)
    return success_response(data={"output": result})


@router.post("/tools/url-encode")
async def url_encode(data: schemas.ToolInput, _=Depends(get_current_user)):
    result = services.url_encode(data.input)
    return success_response(data={"output": result})


@router.post("/tools/url-decode")
async def url_decode(data: schemas.ToolInput, _=Depends(get_current_user)):
    result = services.url_decode(data.input)
    return success_response(data={"output": result})


@router.post("/tools/base64-encode")
async def b64_encode(data: schemas.ToolInput, _=Depends(get_current_user)):
    result = services.b64_encode(data.input)
    return success_response(data={"output": result})


@router.post("/tools/base64-decode")
async def b64_decode(data: schemas.ToolInput, _=Depends(get_current_user)):
    result = services.b64_decode(data.input)
    return success_response(data={"output": result})


@router.post("/tools/timestamp")
async def timestamp_convert(data: schemas.TimestampInput, _=Depends(get_current_user)):
    result = services.timestamp_convert(data.value)
    return success_response(data=result)


@router.post("/tools/regex-test")
async def regex_test(data: schemas.RegexTestInput, _=Depends(get_current_user)):
    result = services.regex_test(data.pattern, data.text, data.flags)
    return success_response(data=result)


@router.post("/tools/ip-query")
async def ip_query(data: schemas.ToolInput, _=Depends(get_current_user)):
    import socket as sock_lib
    try:
        info = sock_lib.getaddrinfo(data.input, None)
        ip_addr = info[0][4][0] if info else data.input
    except Exception:
        ip_addr = "unknown"
    return success_response(data={"ip": data.input, "address_info": ip_addr})


@router.post("/tools/port-check")
async def port_check(data: schemas.PortCheckInput, _=Depends(get_current_user)):
    result = services.check_port(data.host, data.port, data.timeout)
    return success_response(data=result)


@router.get("/tools/uuid")
async def generate_uuid(count: int = Query(1, ge=1, le=100), _=Depends(get_current_user)):
    result = services.generate_uuids(count)
    return success_response(data={"uuids": result})


@router.get("/links")
async def list_links(category: str = Query(None), _=Depends(get_current_user)):
    links = await services.get_links(category)
    return success_response(data={"items": links})


@router.post("/links")
async def create_link(data: schemas.LinkCreate, _=Depends(require_admin)):
    link = await services.create_link(data.model_dump())
    return success_response(data={"id": link.id, "title": link.title})


@router.put("/links/{link_id}")
async def update_link(link_id: int, data: schemas.LinkUpdate, _=Depends(require_admin)):
    link = await services.update_link(link_id, data.model_dump(exclude_unset=True))
    return success_response(data={"id": link.id, "title": link.title})


@router.delete("/links/{link_id}")
async def delete_link(link_id: int, _=Depends(require_admin)):
    await services.delete_link(link_id)
    return success_response(message="链接已删除")
