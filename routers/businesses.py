"""
Businesses router
"""

from fastapi import APIRouter, HTTPException, Query
from uuid import UUID

from database import db_service
from models import BusinessCreate, BusinessResponse, BusinessUpdate

router = APIRouter(
    prefix='/api/v1/businesses',
    tags=['Businesses'],
)


@router.get('/', response_model=dict, summary="List all businesses")
@router.get('', response_model=dict, include_in_schema=False)
async def list_businesses(
    limit: int = Query(50, ge=1, le=500, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
):
    """Return a paginated list of all businesses."""
    results = await db_service.list_businesses(limit=limit, offset=offset)
    return {
        "total": len(results),
        "limit": limit,
        "offset": offset,
        "data": results,
    }


@router.get('/{business_id}', response_model=BusinessResponse, summary="Get business by ID")
async def get_business(business_id: UUID):
    """Return full details of a single business by its UUID."""
    result = await db_service.get_business(str(business_id))
    if not result:
        raise HTTPException(status_code=404, detail='Business not found')
    return result


@router.post('/', response_model=BusinessResponse, status_code=201, summary="Create a business")
@router.post('', response_model=BusinessResponse, status_code=201, include_in_schema=False)
async def create_business(business: BusinessCreate):
    result = await db_service.create_business(business.model_dump())
    if not result:
        raise HTTPException(status_code=500, detail='Unable to create business')
    return result


@router.put('/{business_id}', response_model=BusinessResponse, summary="Update a business")
async def update_business(business_id: UUID, business_update: BusinessUpdate):
    update_data = {k: v for k, v in business_update.model_dump().items() if v is not None}
    result = await db_service.update_business(str(business_id), update_data)
    if not result:
        raise HTTPException(status_code=404, detail='Business not found')
    return result


@router.delete('/{business_id}', response_model=BusinessResponse, summary="Delete (deactivate) a business")
async def delete_business(business_id: UUID):
    result = await db_service.delete_business(str(business_id))
    if not result:
        raise HTTPException(status_code=404, detail='Business not found')
    return result
