import uvicorn
from fastapi import FastAPI
from ksm_core.config import settings
from ksm_core.database import init_db, close_db
from ksm_core.middleware import RequestIDMiddleware
from ksm_core.exceptions import AppException, global_exception_handler, unhandled_exception_handler
from ksm_core.rate_limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from ksm_core.response import success_response
from ksm_gateway.routes import router as gateway_router

app = FastAPI(title="K8s Secret Manager API Gateway", version=settings.APP_VERSION, docs_url="/docs")
app.add_middleware(RequestIDMiddleware)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(AppException, global_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
app.include_router(gateway_router, prefix="/api/v1")


@app.on_event("startup")
async def startup():
    await init_db()


@app.on_event("shutdown")
async def shutdown():
    await close_db()


@app.get("/health")
async def health():
    return success_response(data={"status": "ok", "service": "api-gateway"})


if __name__ == "__main__":
    uvicorn.run("ksm_gateway.main:app", host="0.0.0.0", port=settings.GATEWAY_PORT)
