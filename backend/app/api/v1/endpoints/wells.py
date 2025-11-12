"""
Well management endpoints
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from app.schemas.well import Well, WellResponse
from app.services.well_service import WellService

router = APIRouter()


@router.get("/", response_model=List[WellResponse])
async def get_wells(
    status: Optional[str] = Query(None),
    service: WellService = Depends(),
):
    """Get all wells with optional status filter"""
    return await service.get_wells(status=status)


@router.get("/{well_id}", response_model=WellResponse)
async def get_well(
    well_id: str,
    service: WellService = Depends(),
):
    """Get well by ID"""
    return await service.get_well(well_id)


@router.post("/", response_model=WellResponse)
async def create_well(
    well: Well,
    service: WellService = Depends(),
):
    """Create a new well"""
    return await service.create_well(well)

