from typing import Any, Optional
from fastapi.responses import JSONResponse


def success_response(data: Any = None, message: str = "success", request_id: Optional[str] = None) -> JSONResponse:
    body: dict[str, Any] = {"code": 0, "message": message}
    body["data"] = data
    if request_id:
        body["request_id"] = request_id
    return JSONResponse(status_code=200, content=body)


def paginated_response(items: list, total: int, page: int, size: int, request_id: Optional[str] = None) -> JSONResponse:
    pages = (total + size - 1) // size if size > 0 else 0
    data = {"items": items, "total": total, "page": page, "size": size, "pages": pages}
    body: dict[str, Any] = {"code": 0, "message": "success", "data": data}
    if request_id:
        body["request_id"] = request_id
    return JSONResponse(status_code=200, content=body)


def error_response(code: int, message: str, status_code: int = 400, detail: Any = None, request_id: Optional[str] = None) -> JSONResponse:
    body: dict[str, Any] = {"code": code, "message": message}
    if detail:
        body["detail"] = detail
    if request_id:
        body["request_id"] = request_id
    return JSONResponse(status_code=status_code, content=body)
