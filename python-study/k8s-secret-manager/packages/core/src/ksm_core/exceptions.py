from fastapi import Request
from ksm_core.response import error_response


class AppException(Exception):
    def __init__(self, code: int, message: str, status_code: int = 400, detail=None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.detail = detail


class NotFoundException(AppException):
    def __init__(self, message: str = "资源不存在"):
        super().__init__(code=40400, message=message, status_code=404)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "未授权"):
        super().__init__(code=40100, message=message, status_code=401)


class ForbiddenException(AppException):
    def __init__(self, message: str = "无权限"):
        super().__init__(code=40300, message=message, status_code=403)


class BadRequestException(AppException):
    def __init__(self, message: str = "请求参数错误", detail=None):
        super().__init__(code=40000, message=message, status_code=400, detail=detail)


async def global_exception_handler(request: Request, exc: AppException):
    return error_response(
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        detail=exc.detail,
        request_id=getattr(request.state, "request_id", None),
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    return error_response(
        code=50000,
        message="服务器内部错误",
        status_code=500,
        request_id=getattr(request.state, "request_id", None),
    )
