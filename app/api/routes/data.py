from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK

from app.api.dependencies.data import get_data_dep, put_data_dep, delete_data_dep, download_data_dep
from app.api.routes.constants import Routes
from app.schemas import GlobalResponse

router = APIRouter(prefix="/v1/data")


# @router.get("/get", name=Routes.DATA_GET, status_code=HTTP_200_OK)
# async def put_data(tracker_response: GlobalResponse = Depends(get_data_dep)):
#     return tracker_response


# @router.post("/put", name=Routes.DATA_PUT, status_code=HTTP_200_OK)
# async def put_data(tracker_response: GlobalResponse = Depends(put_data_dep)):
#     return tracker_response

@router.get("/get", name=Routes.GET_DATA, status_code=HTTP_200_OK)
async def download_data(tracker_response: GlobalResponse = Depends(get_data_dep)):
    return tracker_response


@router.get("/download", name=Routes.DOWNLOAD_DATA, status_code=HTTP_200_OK)
async def download_data(tracker_response: GlobalResponse = Depends(download_data_dep)):
    return tracker_response


@router.delete("/delete", name=Routes.DATA_DELETE, status_code=HTTP_200_OK)
async def delete_data(tracker_response: GlobalResponse = Depends(delete_data_dep)):
    return tracker_response
