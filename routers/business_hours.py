"""
Business hours router
Endpoints for CRUD operations on business hours
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from uuid import UUID

from database import db_service
from models import BusinessHoursCreate, BusinessHoursResponse, BusinessHoursUpdate

router = APIRouter(
    prefix='/api/v1/business-hours',
    tags=['Business Hours'],
)

@router.post('/', response_model=BusinessHoursResponse)
async def create_business_hours(hours: BusinessHoursCreate):
    result = await db_service.create_business_hours(hours.model_dump())
    if not result:
        raise HTTPException(status_code=500, detail='Unable to create business hours')
    return result

@router.get('/{hours_id}', response_model=BusinessHoursResponse)
async def get_business_hours(hours_id: UUID):
    result = await db_service.get_business_hours(str(hours_id))
    if not result:
        raise HTTPException(status_code=404, detail='Business hours not found')
    return result

@router.get('/', response_model=List[BusinessHoursResponse])
async def list_business_hours(
    business_id: UUID,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return await db_service.list_business_hours(str(business_id), limit=limit, offset=offset)

@router.put('/{hours_id}', response_model=BusinessHoursResponse)
async def update_business_hours(hours_id: UUID, update: BusinessHoursUpdate):
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    result = await db_service.update_business_hours(str(hours_id), update_data)
    if not result:
        raise HTTPException(status_code=404, detail='Business hours not found')
    return result

@router.delete('/{hours_id}', response_model=BusinessHoursResponse)
async def delete_business_hours(hours_id: UUID):
    result = await db_service.delete_business_hours(str(hours_id))
    if not result:
        raise HTTPException(status_code=404, detail='Business hours not found')
    return result
