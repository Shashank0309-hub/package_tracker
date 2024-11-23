from loguru import logger
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.schemas import GlobalResponse

from app.exceptions.custom import ClientException


async def global_exception(_: Request, exc: Exception) -> JSONResponse:
    logger.exception(exc)
    return JSONResponse(
        {"status": HTTP_500_INTERNAL_SERVER_ERROR, "message": str(exc)},
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def http_global_exception(_: Request, exc: HTTPException) -> JSONResponse:
    logger.exception(exc)
    return JSONResponse(
        GlobalResponse(
            data=exc.detail, status=exc.status_code, message=str(exc)
        ).dict(),
        status_code=exc.status_code,
    )


async def http_service_exception(_: Request, exc: ClientException) -> JSONResponse:
    logger.exception(exc)
    return JSONResponse(
        {
            "status": exc.status_code,
            "message": exc.message,
            "data": exc.data or str(exc.__cause__) if exc.__cause__ else exc.__cause__,
        },
        status_code=exc.status_code,
    )
