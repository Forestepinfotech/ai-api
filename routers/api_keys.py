"""
API keys router
Endpoints for CRUD operations on API keys
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from uuid import UUID

from database import db_service
from models import APIKeyCreate, APIKeyResponse, APIKeyUpdate

router = APIRouter(
    prefix='/api/v1/api-keys',
    tags=['API Keys'],
)

@router.post('/', response_model=APIKeyResponse)
async def create_api_key(api_key: APIKeyCreate):
    result = await db_service.create_api_key(api_key.model_dump())
    if not result:
        raise HTTPException(status_code=500, detail='Unable to create API key')
    return result

@router.get('/{api_key_id}', response_model=APIKeyResponse)
async def get_api_key(api_key_id: UUID):
    result = await db_service.get_api_key(str(api_key_id))
    if not result:
        raise HTTPException(status_code=404, detail='API key not found')
    return result

@router.get('/', response_model=List[APIKeyResponse])
async def list_api_keys(
    business_id: UUID,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return await db_service.list_api_keys(str(business_id), limit=limit, offset=offset)

@router.put('/{api_key_id}', response_model=APIKeyResponse)
async def update_api_key(api_key_id: UUID, api_key_update: APIKeyUpdate):
    update_data = {k: v for k, v in api_key_update.model_dump().items() if v is not None}
    result = await db_service.update_api_key(str(api_key_id), update_data)
    if not result:
        raise HTTPException(status_code=404, detail='API key not found')
    return result

@router.delete('/{api_key_id}', response_model=APIKeyResponse)
async def delete_api_key(api_key_id: UUID):
    result = await db_service.delete_api_key(str(api_key_id))
    if not result:
        raise HTTPException(status_code=404, detail='API key not found')
    return result
