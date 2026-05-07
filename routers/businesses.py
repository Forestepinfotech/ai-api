"""
Businesses router
Endpoints for CRUD operations on businesses
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from uuid import UUID

from database import db_service
from models import BusinessCreate, BusinessResponse, BusinessUpdate

router = APIRouter(
    prefix='/api/v1/businesses',
    tags=['Businesses'],
)

@router.post('/', response_model=BusinessResponse)
async def create_business(business: BusinessCreate):
    result = await db_service.create_business(business.model_dump())
    if not result:
        raise HTTPException(status_code=500, detail='Unable to create business')
    return result

@router.get('/{business_id}', response_model=BusinessResponse)
async def get_business(business_id: UUID):
    result = await db_service.get_business(str(business_id))
    if not result:
        raise HTTPException(status_code=404, detail='Business not found')
    return result

@router.get('/', response_model=List[BusinessResponse])
async def list_businesses(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return await db_service.list_businesses(limit=limit, offset=offset)

@router.put('/{business_id}', response_model=BusinessResponse)
async def update_business(business_id: UUID, business_update: BusinessUpdate):
    update_data = {k: v for k, v in business_update.model_dump().items() if v is not None}
    result = await db_service.update_business(str(business_id), update_data)
    if not result:
        raise HTTPException(status_code=404, detail='Business not found')
    return result

@router.delete('/{business_id}', response_model=BusinessResponse)
async def delete_business(business_id: UUID):
    result = await db_service.delete_business(str(business_id))
    if not result:
        raise HTTPException(status_code=404, detail='Business not found')
    return result
