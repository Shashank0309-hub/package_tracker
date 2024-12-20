from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK

from app.api.routes.constants import Routes
from app.schemas import GlobalResponse
from app.api.dependencies.dashboard import get_dashboard_data_dep, put_additional_data_dep, get_additional_data_dep, \
    get_date_wise_data_dep

router = APIRouter(prefix="/v1/dashboard")


@router.get("/get", name=Routes.DASHBOARD, status_code=HTTP_200_OK)
async def fetch_dashboard_data(dashboard_response: GlobalResponse = Depends(get_dashboard_data_dep)):
    return dashboard_response


@router.post("/additional_data/post", name=Routes.ADDITIONAL_COST, status_code=HTTP_200_OK)
async def put_additional_data(additional_data_response: GlobalResponse = Depends(put_additional_data_dep)):
    return additional_data_response


@router.get("/additional_data/get", name=Routes.FETCH_ADDITIONAL_COST, status_code=HTTP_200_OK)
async def put_additional_data(additional_data_response: GlobalResponse = Depends(get_additional_data_dep)):
    return additional_data_response


@router.get("/date_wise_data/get", name=Routes.FETCH_DATE_WISE_DATA, status_code=HTTP_200_OK)
async def put_additional_data(additional_data_response: GlobalResponse = Depends(get_date_wise_data_dep)):
    return additional_data_response
