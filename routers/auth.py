"""
Authentication router
Register and login endpoints with JWT token generation
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt

from database import db_service
from models import UserCreate, UserResponse, LoginRequest, TokenResponse
from config import settings

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)

_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def _create_access_token(user_id: str, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user_id, "email": email, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    try:
        existing = await db_service.get_user_by_email(user.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        data = user.model_dump()
        data["password_hash"] = _hash_password(data.pop("password"))
        data["role"] = "user"

        result = await db_service.create_user(data)
        if not result:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to create user")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    try:
        user = await db_service.get_user_by_email(credentials.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        if not _verify_password(credentials.password, user.get("password_hash", "")):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        if not user.get("is_active", True):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

        await db_service.update_user(str(user["id"]), {"last_login_at": datetime.now(timezone.utc).isoformat()})

        token = _create_access_token(str(user["id"]), user["email"])
        return TokenResponse(
            access_token=token,
            user_id=str(user["id"]),
            email=user["email"],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
