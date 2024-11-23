from app.schemas import GlobalResponse
from app.services.dashboard import DashboardService


async def get_dashboard_data_dep():
    response = await DashboardService().get_dashboard_data_service()

    return GlobalResponse(
        data=response
    )
