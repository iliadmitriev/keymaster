"""
Login views handlers.
"""
import uuid
from datetime import timedelta

from fastapi import APIRouter, HTTPException
from sqlalchemy.future import select
from starlette import status
from starlette.requests import Request

from config.auth import ACCESS_TOKEN_EXPIRE, REFRESH_TOKEN_EXPIRE
from db.redis import set_redis_key
from models import User
from schemas import Auth, Register, UserCreate
from schemas.login import Token
from schemas.users import UserOut
from utils.auth import create_access_token
from utils.password import password_hash_ctx

router = APIRouter()


@router.post(
    "/login/register/",
    name="login:register",
    summary="Register a new user",
    status_code=status.HTTP_200_OK,
    description="Registers new user",
    response_model=UserOut,
)
async def login_register(register: Register, request: Request) -> User:
    """View function for creating a new unprivileged user from registration.

    Args:
        register: user data login and password
        request: request instance

    Returns:
        a newly registered user from DB
    """
    db = request.app.state.db
    res = await db.execute(select(User).filter(User.email == register.email))
    found_users = res.scalar_one_or_none()
    if found_users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{register.email}' already exists",
        )
    user = UserCreate.model_validate(register.model_dump())
    user.password = password_hash_ctx.hash(register.password)
    user_db = User(**user.model_dump())
    db.add(user_db)
    await db.commit()
    await db.refresh(user_db)
    return user_db


@router.post(
    "/login/auth/",
    name="login:auth",
    summary="Auth user",
    status_code=status.HTTP_200_OK,
    description="Auth user and get access and refresh tokens",
    response_model=Token,
)
async def login_auth(auth: Auth, request: Request) -> Token:
    """Login view handler function.

    Args:
        auth: incoming auth data
        request: incoming request

    Returns:
        JWT token
    """
    res = await request.app.state.db.execute(
        select(User).filter(User.email == auth.email)
    )
    db_user = res.scalar()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if not password_hash_ctx.verify(auth.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    token = {
        "id": db_user.id,
        "email": db_user.email,
        "jti": uuid.uuid4().hex,
    }
    if db_user.is_superuser:
        token.update({"scope": ["admin"]})
    access_token = {**token, "token_type": "access_token"}
    refresh_token = {**token, "token_type": "refresh_token"}
    token = Token(
        access_token=create_access_token(
            access_token, timedelta(seconds=ACCESS_TOKEN_EXPIRE)
        ),
        refresh_token=create_access_token(
            refresh_token, timedelta(seconds=REFRESH_TOKEN_EXPIRE)
        ),
    )
    await set_redis_key(
        request.app.state.redis, token.refresh_token, "1", REFRESH_TOKEN_EXPIRE
    )

    return token
