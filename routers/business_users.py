"""
Business users router
Endpoints for CRUD operations on business users
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from uuid import UUID

from database import db_service
from models import BusinessUserCreate, BusinessUserResponse, BusinessUserUpdate

router = APIRouter(
    prefix='/api/v1/business-users',
    tags=['Business Users'],
)

@router.post('/', response_model=BusinessUserResponse)
async def create_business_user(business_user: BusinessUserCreate):
    result = await db_service.create_business_user(business_user.model_dump())
    if not result:
        raise HTTPException(status_code=500, detail='Unable to create business user')
    return result

@router.get('/{business_user_id}', response_model=BusinessUserResponse)
async def get_business_user(business_user_id: UUID):
    result = await db_service.get_business_user(str(business_user_id))
    if not result:
        raise HTTPException(status_code=404, detail='Business user not found')
    return result

@router.get('/', response_model=List[BusinessUserResponse])
async def list_business_users(
    business_id: UUID,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return await db_service.list_business_users(str(business_id), limit=limit, offset=offset)

@router.put('/{business_user_id}', response_model=BusinessUserResponse)
async def update_business_user(business_user_id: UUID, update: BusinessUserUpdate):
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    result = await db_service.update_business_user(str(business_user_id), update_data)
    if not result:
        raise HTTPException(status_code=404, detail='Business user not found')
    return result

@router.delete('/{business_user_id}', response_model=BusinessUserResponse)
async def delete_business_user(business_user_id: UUID):
    result = await db_service.delete_business_user(str(business_user_id))
    if not result:
        raise HTTPException(status_code=404, detail='Business user not found')
    return result
