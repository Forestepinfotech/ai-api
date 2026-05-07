"""
FAQs router
Endpoints for CRUD operations on FAQs
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from uuid import UUID

from database import db_service
from models import FAQCreate, FAQResponse, FAQUpdate

router = APIRouter(
    prefix='/api/v1/faqs',
    tags=['FAQs'],
)

@router.post('/', response_model=FAQResponse)
async def create_faq(faq: FAQCreate):
    result = await db_service.create_faq(faq.model_dump())
    if not result:
        raise HTTPException(status_code=500, detail='Unable to create FAQ')
    return result

@router.get('/{faq_id}', response_model=FAQResponse)
async def get_faq(faq_id: UUID):
    result = await db_service.get_faq(str(faq_id))
    if not result:
        raise HTTPException(status_code=404, detail='FAQ not found')
    return result

@router.get('/', response_model=List[FAQResponse])
async def list_faqs(
    business_id: UUID,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return await db_service.list_faqs(str(business_id), limit=limit, offset=offset)

@router.put('/{faq_id}', response_model=FAQResponse)
async def update_faq(faq_id: UUID, faq_update: FAQUpdate):
    update_data = {k: v for k, v in faq_update.model_dump().items() if v is not None}
    result = await db_service.update_faq(str(faq_id), update_data)
    if not result:
        raise HTTPException(status_code=404, detail='FAQ not found')
    return result

@router.delete('/{faq_id}', response_model=FAQResponse)
async def delete_faq(faq_id: UUID):
    result = await db_service.delete_faq(str(faq_id))
    if not result:
        raise HTTPException(status_code=404, detail='FAQ not found')
    return result
