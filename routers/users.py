"""
Users router
"""

from fastapi import APIRouter, HTTPException, Query
from uuid import UUID
import bcrypt

from database import db_service
from models import UserCreate, UserResponse, UserUpdate

router = APIRouter(
    prefix='/api/v1/users',
    tags=['Users'],
)


@router.get('/', response_model=dict, summary="List all users")
@router.get('', response_model=dict, include_in_schema=False)
async def list_users(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    results = await db_service.list_users(limit=limit, offset=offset)
    return {
        "total": len(results),
        "limit": limit,
        "offset": offset,
        "data": results,
    }


@router.get('/{user_id}', response_model=UserResponse, summary="Get user by ID")
async def get_user(user_id: UUID):
    result = await db_service.get_user(str(user_id))
    if not result:
        raise HTTPException(status_code=404, detail='User not found')
    return result


@router.post('/', response_model=UserResponse, status_code=201, summary="Create user")
@router.post('', response_model=UserResponse, status_code=201, include_in_schema=False)
async def create_user(user: UserCreate):
    existing = await db_service.get_user_by_email(user.email)
    if existing:
        raise HTTPException(status_code=409, detail='Email already registered')
    data = user.model_dump()
    data["password_hash"] = bcrypt.hashpw(data.pop("password").encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    data["role"] = "user"
    result = await db_service.create_user(data)
    if not result:
        raise HTTPException(status_code=500, detail='Unable to create user')
    return result


@router.put('/{user_id}', response_model=UserResponse, summary="Update user")
async def update_user(user_id: UUID, user_update: UserUpdate):
    update_data = {k: v for k, v in user_update.model_dump().items() if v is not None}
    result = await db_service.update_user(str(user_id), update_data)
    if not result:
        raise HTTPException(status_code=404, detail='User not found')
    return result


@router.delete('/{user_id}', response_model=UserResponse, summary="Delete user")
async def delete_user(user_id: UUID):
    result = await db_service.delete_user(str(user_id))
    if not result:
        raise HTTPException(status_code=404, detail='User not found')
    return result
