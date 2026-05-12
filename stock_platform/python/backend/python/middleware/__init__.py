import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestContextMiddleware(BaseHTTPMiddleware):
    """请求上下文中间件，为每个请求添加 request_id 和处理时间"""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        start_time = time.time()

        # 将 request_id 存入 request.state 供后续使用
        request.state.request_id = request_id

        # 执行后续处理
        response = await call_next(request)

        # 计算处理时间
        process_time = time.time() - start_time

        # 添加响应头
        response.headers["x-request-id"] = request_id
        response.headers["x-process-time"] = f"{process_time:.4f}s"

        return response