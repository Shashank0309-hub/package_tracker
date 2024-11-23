import time

from fastapi import FastAPI
from loguru import logger
from pydantic import ValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.api.errors.validation_error import http422_error_handler
from app.api.routes.api import router as api_router
from app.core.config import VERSION, SERVICE_NAME, DEBUG, OPENAPI_PREFIX, ALLOWED_HOSTS
from app.core.events import create_start_app_handler, create_stop_app_handler
from app.exceptions import (global_exception, http_global_exception,
                            http_service_exception)
from app.exceptions.custom import SearchException, ClientException

from app.core.strings import INTERNAL_SERVER_ERROR

logger.add(
    sink="/tmp/access.{time:YYYY_MM_DD}.log",
    rotation="7 days",
    retention="3 days",
    format="{time:DD/MMM/YYYY:HH:mm:ss ZZZ} {message}",
)


def get_application() -> FastAPI:

    application = FastAPI(
        title=SERVICE_NAME,
        debug=DEBUG,
        version=VERSION,
        openapi_prefix=OPENAPI_PREFIX,
    )

    application.add_event_handler("startup", create_start_app_handler(application))
    application.add_event_handler("shutdown", create_stop_app_handler(application))

    application.add_exception_handler(Exception, global_exception)
    application.add_exception_handler(HTTPException, http_global_exception)
    application.add_exception_handler(ValidationError, http422_error_handler)
    application.add_exception_handler(ClientException, http_service_exception)
    application.add_exception_handler(SearchException, http_service_exception)
    application.include_router(api_router)

    @application.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        try:
            start_time = time.time()
            response = await call_next(request)
            process_time = round(round((time.time() - start_time) * 1000, 2))
            response.headers["X-Process-Time"] = str(process_time) + " ms"
            logger.info("{0} took time {1} ms", request.url.path, process_time)
            return response

        except Exception as exc:
            logger.exception(exc)
            return JSONResponse(
                {
                    "message": INTERNAL_SERVER_ERROR,
                    "status": HTTP_500_INTERNAL_SERVER_ERROR,
                },
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_HOSTS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return application


app = get_application()
