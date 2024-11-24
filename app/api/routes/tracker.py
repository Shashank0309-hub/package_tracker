from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK

# from app.api.dependencies.tracker import fetch_tracker_data_dep
from app.api.dependencies.tracker import get_tracker_data_dep, get_pincode_sku_data_dep, get_rto_data_dep, \
    get_payment_data_dep
from app.api.routes.constants import Routes
from app.schemas import GlobalResponse

router = APIRouter(prefix="/v1/tracker")


# @router.post("/fetch", name=Routes.TRACKER, status_code=HTTP_200_OK)
# async def fetch_tracker_data(tracker_response: GlobalResponse = Depends(fetch_tracker_data_dep)):
#     return tracker_response


@router.post("/get", name=Routes.TRACKER, status_code=HTTP_200_OK)
async def fetch_tracker_data(tracker_response: GlobalResponse = Depends(get_tracker_data_dep)):
    return tracker_response


@router.get("/pincode_sku", name=Routes.PINCODE_SKU, status_code=HTTP_200_OK)
async def fetch_pincode_sku(tracker_response: GlobalResponse = Depends(get_pincode_sku_data_dep)):
    return tracker_response


@router.get("/rto", name=Routes.RTO_DATA, status_code=HTTP_200_OK)
async def fetch_rto(tracker_response: GlobalResponse = Depends(get_rto_data_dep)):
    return tracker_response


@router.post("/payment", name=Routes.PAYMENT_DATA, status_code=HTTP_200_OK)
async def fetch_payment(tracker_response: GlobalResponse = Depends(get_payment_data_dep)):
    return tracker_response
