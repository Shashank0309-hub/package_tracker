import io
from datetime import date, datetime, timedelta
from typing import Optional, Union

from fastapi import UploadFile, File
from starlette.responses import StreamingResponse

from app.schemas import GlobalResponse

from app.schemas.tracker import CourierPartnerName
from app.services.data import DataService


async def get_data_dep(
        courier_partner: CourierPartnerName,
):
    response = await DataService().get_data_service(courier_partner)

    return GlobalResponse(
        data=response
    )


async def put_data_dep(
        courier_partner: CourierPartnerName,
        order_id: Optional[str] = None,
        consignment_id: Optional[str] = None,
        product_name: Optional[str] = None,
        customer_number: Optional[int] = None,
        customer_address: Optional[str] = None,
        customer_pincode: Optional[int] = None,
        product_price: Optional[float] = None,
        date: Optional[str] = None,
        status: Optional[str] = None,
        upload_file: Optional[UploadFile] = None,
):
    response = await DataService().put_data_service(
        order_id=order_id,
        consignment_id=consignment_id,
        product_name=product_name,
        courier_partner=courier_partner,
        customer_number=customer_number,
        customer_address=customer_address,
        customer_pincode=customer_pincode,
        product_price=product_price,
        date=date,
        status=status,
        upload_file=upload_file,
    )

    return GlobalResponse(
        data=response
    )


async def delete_data_dep(
        courier_partner: CourierPartnerName,
        order_id: Optional[str] = None,
        full_data: Optional[bool] = False,
):
    response = await DataService().delete_data_service(
        courier_partner=courier_partner,
        order_id=order_id,
        full_data=full_data,
    )

    return GlobalResponse(
        data=response
    )


async def download_data_dep(
        courier_partner: CourierPartnerName,
        start_date: Optional[Union[datetime, date]] = datetime.now() - timedelta(days=90),
        end_date: Optional[Union[datetime, date]] = datetime.now(),
):
    df, file_name = await DataService().download_data_service(
        courier_partner=courier_partner,
        start_date=start_date,
        end_date=end_date,
    )

    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    return StreamingResponse(iter([csv_buffer.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition": f"attachment; filename={file_name}"})

    # return GlobalResponse(
    #     data=response
    # )
