from fastapi import APIRouter

from app.api.routes import tracker, service, data, dashboard

router = APIRouter()

router.include_router(dashboard.router, tags=["Dashboard"])
router.include_router(tracker.router, tags=["Tracker"])
router.include_router(data.router, tags=["Data"])
router.include_router(service.router, tags=["Metrics"])
