from datetime import datetime, date, timedelta
from typing import Optional, Union

from app.schemas import GlobalResponse
from app.schemas.dashboard import AdditionalDataReq
from app.schemas.tracker import CourierPartnerName
from app.services.dashboard import DashboardService


async def get_dashboard_data_dep(selected_courier_partner: Optional[CourierPartnerName] = None):
    response = await DashboardService().get_dashboard_data_service(
        selected_courier_partner=selected_courier_partner
    )

    return GlobalResponse(
        data=response
    )


async def put_additional_data_dep(request: AdditionalDataReq, courier_partner: Optional[CourierPartnerName] = None):
    response = await DashboardService().put_additional_data_service(
        courier_partner=courier_partner,
        request=request
    )

    return GlobalResponse(
        data=response
    )


async def get_additional_data_dep(courier_partner: Optional[CourierPartnerName] = None):
    response = await DashboardService().get_additional_data_service(
        courier_partner=courier_partner,
    )

    return GlobalResponse(
        data=response
    )


async def get_date_wise_data_dep(
        courier_partner: Optional[CourierPartnerName] = None,
        start_date: Optional[Union[datetime, date]] = datetime.now() - timedelta(days=7),
        end_date: Optional[Union[datetime, date]] = datetime.now(),
):
    response = await DashboardService().get_date_wise_data_service(
        selected_courier_partner=courier_partner,
        start_date=start_date,
        end_date=end_date,
    )

    return GlobalResponse(
        data=response
    )
