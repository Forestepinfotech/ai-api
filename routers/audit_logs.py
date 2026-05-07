"""
Audit logs router
Endpoints for CRUD operations on audit logs
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID

from database import db_service
from models import AuditLogCreate, AuditLogResponse

router = APIRouter(
    prefix='/api/v1/audit-logs',
    tags=['Audit Logs'],
)

@router.post('/', response_model=AuditLogResponse)
async def create_audit_log(audit_log: AuditLogCreate):
    result = await db_service.create_audit_log(audit_log.model_dump())
    if not result:
        raise HTTPException(status_code=500, detail='Unable to create audit log')
    return result

@router.get('/{audit_log_id}', response_model=AuditLogResponse)
async def get_audit_log(audit_log_id: UUID):
    result = await db_service.get_audit_log(str(audit_log_id))
    if not result:
        raise HTTPException(status_code=404, detail='Audit log not found')
    return result

@router.get('/', response_model=List[AuditLogResponse])
async def list_audit_logs(
    business_id: Optional[UUID] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    business_id_value = str(business_id) if business_id else None
    return await db_service.list_audit_logs(business_id_value, limit=limit, offset=offset)

@router.delete('/{audit_log_id}', response_model=AuditLogResponse)
async def delete_audit_log(audit_log_id: UUID):
    result = await db_service.delete_audit_log(str(audit_log_id))
    if not result:
        raise HTTPException(status_code=404, detail='Audit log not found')
    return result
