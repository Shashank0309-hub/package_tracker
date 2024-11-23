from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK

from app.api.routes.constants import Routes
from app.schemas import GlobalResponse
from app.api.dependencies.dashboard import get_dashboard_data_dep

router = APIRouter(prefix="/v1/dashboard")


@router.get("/get", name=Routes.DASHBOARD, status_code=HTTP_200_OK)
async def fetch_dashboard_data(dashboard_response: GlobalResponse = Depends(get_dashboard_data_dep)):
    return dashboard_response
