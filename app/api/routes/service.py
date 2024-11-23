from fastapi import APIRouter
from starlette.status import HTTP_200_OK

from app.api.routes.constants import Routes


router = APIRouter()


@router.get("/live", name=Routes.CHECK_DEPENDENCIES, status_code=HTTP_200_OK)
async def check_dependencies() -> str:
    """
    Liveness endpoint
    """
    return "Live!"
