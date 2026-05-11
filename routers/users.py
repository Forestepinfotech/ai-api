"""
Users router
Endpoints for CRUD operations on users
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from uuid import UUID
from passlib.context import CryptContext

from database import db_service
from models import UserCreate, UserResponse, UserUpdate

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix='/api/v1/users',
    tags=['Users'],
)

@router.post('/', response_model=UserResponse)
async def create_user(user: UserCreate):
    existing = await db_service.get_user_by_email(user.email)
    if existing:
        raise HTTPException(status_code=409, detail='Email already registered')
    data = user.model_dump()
    data["password_hash"] = _pwd_context.hash(data.pop("password"))
    data["role"] = "user"
    result = await db_service.create_user(data)
    if not result:
        raise HTTPException(status_code=500, detail='Unable to create user')
    return result

@router.get('/{user_id}', response_model=UserResponse)
async def get_user(user_id: UUID):
    result = await db_service.get_user(str(user_id))
    if not result:
        raise HTTPException(status_code=404, detail='User not found')
    return result

@router.get('/', response_model=List[UserResponse])
async def list_users(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return await db_service.list_users(limit=limit, offset=offset)

@router.put('/{user_id}', response_model=UserResponse)
async def update_user(user_id: UUID, user_update: UserUpdate):
    update_data = {k: v for k, v in user_update.model_dump().items() if v is not None}
    result = await db_service.update_user(str(user_id), update_data)
    if not result:
        raise HTTPException(status_code=404, detail='User not found')
    return result

@router.delete('/{user_id}', response_model=UserResponse)
async def delete_user(user_id: UUID):
    result = await db_service.delete_user(str(user_id))
    if not result:
        raise HTTPException(status_code=404, detail='User not found')
    return result
