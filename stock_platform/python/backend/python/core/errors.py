from typing import Any, Optional


class AppError(Exception):
    """统一错误基类"""

    def __init__(self, message: str, code: str = "error", details: Optional[dict] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(AppError):
    """资源未找到错误"""

    def __init__(self, message: str = "资源未找到"):
        super().__init__(message, code="not_found")


class ValidationError(AppError):
    """数据验证错误"""

    def __init__(self, message: str = "数据验证失败", details: Optional[dict] = None):
        super().__init__(message, code="validation_error", details=details)


class AlreadyExistsError(AppError):
    """资源已存在错误"""

    def __init__(self, message: str = "资源已存在"):
        super().__init__(message, code="already_exists")


class UnauthorizedError(AppError):
    """未授权错误"""

    def __init__(self, message: str = "未授权"):
        super().__init__(message, code="unauthorized")


class InternalServerError(AppError):
    """服务器内部错误"""

    def __init__(self, message: str = "服务器内部错误"):
        super().__init__(message, code="internal_error")


def register_exception_handlers(app):
    """注册全局异常处理器到 FastAPI app"""
    from fastapi.responses import JSONResponse

    @app.exception_handler(AppError)
    async def app_error_handler(request, exc: AppError):
        return JSONResponse(
            status_code=400,
            content={
                "error": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request, exc: NotFoundError):
        return JSONResponse(
            status_code=404,
            content={
                "error": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request, exc: ValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(AlreadyExistsError)
    async def already_exists_handler(request, exc: AlreadyExistsError):
        return JSONResponse(
            status_code=409,
            content={
                "error": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_handler(request, exc: UnauthorizedError):
        return JSONResponse(
            status_code=401,
            content={
                "error": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(InternalServerError)
    async def internal_error_handler(request, exc: InternalServerError):
        return JSONResponse(
            status_code=500,
            content={
                "error": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        )