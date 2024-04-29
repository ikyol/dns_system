import asyncio
import uvloop
import sentry_sdk

from loguru import logger
from fastapi import FastAPI
from starlette import status
from pydantic import ValidationError
from starlette.requests import Request
from sqlalchemy.exc import NoResultFound
from fastapi.encoders import jsonable_encoder
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from dns_system.routers.api import core_router
from dns_system.config.settings import settings
from dns_system.config.log_config import conf, set_datetime
from dns_system.utils.exceptions import not_found_exception_handler

# set base log format
logger.remove()
logger.configure(**conf, patcher=set_datetime)

if settings.DSN:
    sentry_sdk.init(dsn=settings.DSN, traces_sample_rate=1.0, profiles_sample_rate=1.0)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


#: FastAPI инстанс для открытого API проекта
api_app = FastAPI(
    title=f"{settings.PROJECT_NAME} API",
    openapi_url="/docs/openapi.json",
    docs_url="/docs/swagger.yml"
)

api_app.include_router(core_router, prefix=settings.CURRENT_API_VERSION, tags=["api_v1"])

#: Основной FastAPI инстанс
app = FastAPI(
    title=f"{settings.PROJECT_NAME} root app",
    openapi_url=None,
    docs_url=None
)

app.mount(settings.API_ROUTE_STR, api_app)
# register exceptions
api_app.add_exception_handler(NoResultFound, not_found_exception_handler)
for exc_tuple in settings.EXCEPTIONS_TO_HANDLE:
    app.add_exception_handler(exc_tuple[0], exc_tuple[1])


class ExceptionMiddleware(BaseHTTPMiddleware):
    """Middleware для отлавливания ошибок в ответе от бэкенда"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            response = await call_next(request)
        except ValidationError as e:
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": jsonable_encoder(e.errors())}
            )
        return response


api_app.add_middleware(ExceptionMiddleware)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
