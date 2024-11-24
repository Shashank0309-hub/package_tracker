from typing import Optional

from fastapi import UploadFile, File

from app.schemas import GlobalResponse, Pagination, PaginatedResponse
from app.schemas.tracker import CourierPartnerName
from app.services.tracker import TrackerService


# async def fetch_tracker_data_dep(
#         courier_partner: CourierPartnerName,
#         page: int = 0,
#         limit: int = 25,
#         upload_file: UploadFile = File(...),
# ):
#     response, total = await TrackerService().fetch_tracker_data_service(
#         courier_partner=courier_partner,
#         page=page,
#         limit=limit,
#         upload_file=upload_file,
#     )
#
#     return PaginatedResponse(
#         data=response,
#         message="Successfully Fetched !",
#         meta=Pagination(
#             page=page,
#             limit=limit,
#             total=total,
#         )
#     )


async def get_tracker_data_dep(
        courier_partner: CourierPartnerName,
        page: int = 0,
        limit: int = 25,
        upload_file: UploadFile = File(...),
):
    response, total = await TrackerService().get_tracker_data_service(
        courier_partner=courier_partner,
        page=page,
        limit=limit,
        upload_file=upload_file,
    )

    return PaginatedResponse(
        data=response,
        message="Successfully Fetched !",
        meta=Pagination(
            page=page,
            limit=limit,
            total=total,
        )
    )


async def get_pincode_sku_data_dep(
        courier_partner: CourierPartnerName,
        pincode: Optional[int] = None,
):
    response = await TrackerService().get_pincode_sku_data_service(
        courier_partner=courier_partner,
        pincode=pincode,
    )

    return GlobalResponse(
        data=response
    )


async def get_rto_data_dep(
        courier_partner: CourierPartnerName,
        pincode: Optional[int] = None,
):
    response = await TrackerService().get_rto_data_service(
        courier_partner=courier_partner,
        pincode=pincode,
    )

    return GlobalResponse(
        data=response
    )


async def get_payment_data_dep(
        courier_partner: CourierPartnerName,
        payment_received: Optional[bool] = None,
        cod: Optional[bool] = None,
        page_limit: bool = True,
        page: int = 0,
        limit: int = 25,
        order_id: Optional[str] = None,
        upload_file: UploadFile = File(...),
):
    response = await TrackerService().get_payment_data_service(
        courier_partner=courier_partner,
        payment_received=payment_received,
        cod=cod,
        page_limit=page_limit,
        page=page,
        limit=limit,
        order_id=order_id,
        upload_file=upload_file,
    )

    return GlobalResponse(
        data=response
    )
