from fastapi.routing import APIRouter

from myfi_backend.web.api import docs, dummy, echo, investment, monitoring, otp, redis

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(docs.router)
api_router.include_router(otp.router, prefix="/user", tags=["user"])
api_router.include_router(investment.router, prefix="/investment", tags=["investment"])
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
api_router.include_router(redis.router, prefix="/redis", tags=["redis"])
