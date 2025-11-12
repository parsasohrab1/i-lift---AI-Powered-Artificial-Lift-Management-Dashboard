"""
Dashboard endpoints
"""
from fastapi import APIRouter, Depends

from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/overview")
async def get_dashboard_overview(
    service: DashboardService = Depends(),
):
    """Get dashboard overview data"""
    return await service.get_overview()


@router.get("/summary")
async def get_dashboard_summary(
    service: DashboardService = Depends(),
):
    """Get dashboard summary statistics"""
    return await service.get_summary()

