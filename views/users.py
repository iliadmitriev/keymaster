"""
Users views handle functions.
"""
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from sqlalchemy.future import select
from starlette import status
from starlette.requests import Request

from models.users import User
from schemas.users import UserCreate, UserDB, UserOut, UserUpdate
from utils.password import password_hash_ctx

router = APIRouter()


@router.get(
    "/users/",
    name="users:get",
    summary="get list of users",
    status_code=status.HTTP_200_OK,
    description="get list of users with limit and skip page",
    response_model=List[UserOut],
)
async def user_get_list(
    request: Request, skip: int = 0, limit: int = 50
) -> List[tuple]:
    """Get user list of users request handler.

    Args:
        request: incoming request
        skip: page number
        limit: items per page

    Returns:
        list of found tuples
    """
    db = request.app.state.db
    res = await db.execute(select(User).offset(skip).limit(limit))
    found_users = res.scalars().all()
    return found_users


@router.post(
    "/users/",
    name="users:post",
    summary="create a new user",
    status_code=status.HTTP_201_CREATED,
    description="Creates a new user with post query",
    response_model=UserDB,
)
async def user_post(user: UserCreate, request: Request) -> Optional[User]:
    """Post query handler for creating a new user.

    Args:
        user: user data
        request: incoming request

    Returns:
        created user from db
    """
    db = request.app.state.db
    res = await db.execute(select(User).filter(User.email == user.email))
    found_users = res.scalar_one_or_none()
    if found_users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{user.email}' already exists",
        )
    user_db = User(**user.model_dump())
    user_db.password = password_hash_ctx.hash(user_db.password)
    db.add(user_db)
    await db.commit()
    await db.refresh(user_db)
    return user_db


@router.get(
    "/users/{user_id}",
    name="users:get-by-id",
    summary="get user by id",
    response_model=UserDB,
)
async def user_get_by_id(user_id: int, request: Request) -> Optional[UserDB]:
    """Get user by id from DB handler.

    Args:
        user_id: incoming user id
        request: incoming request

    Returns:
        user from db, or None of not found
    """
    res = await request.app.state.db.execute(
        select(User).filter(User.id == user_id)
    )
    db_user = res.scalar()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return db_user


@router.put(
    "/users/{user_id}",
    name="users:put",
    summary="update user data by id overwriting all attributes",
    response_model=UserDB,
)
async def user_put(
    user_id: int, user: UserUpdate, request: Request
) -> Optional[UserDB]:
    """Update user in db request handler.

    Args:
        user_id: updating user id
        user: new user data
        request: incoming request

    Returns:
        updated user from DB
    """
    found_user = await update_user_field(
        request, user, user_id, exclude_none=True
    )
    return found_user


@router.patch(
    "/users/{user_id}",
    name="users:patch",
    summary="partially update user attributes by id",
    response_model=UserDB,
)
async def user_patch(
    user_id: int, user: UserUpdate, request: Request
) -> Optional[UserDB]:
    """Partial patch user in db request handler.

    Args:
        user_id: user id to patch
        user: partial data to be updated
        request: incoming request

    Returns:
        updated user from DB
    """
    found_user = await update_user_field(
        request, user, user_id, exclude_unset=True
    )
    return found_user


async def update_user_field(
    request: Request, user: UserUpdate, user_id: int, **kwargs
) -> Optional[UserDB]:
    """Update user in db.

    Args:
        request: incoming request
        user: user data to be updated
        user_id: user id to be updated
        **kwargs: key value arguments

    Returns:
        updated user from DB
    """
    db = request.app.state.db
    res = await db.execute(select(User).filter(User.id == user_id))
    found_user = res.scalar_one_or_none()
    if not found_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found",
        )
    for var, value in user.model_dump(**kwargs).items():
        setattr(found_user, var, value)
    if user.model_dump(exclude_none=True).get("password") is not None:
        found_user.password = password_hash_ctx.hash(user.password)
    db.add(found_user)
    await db.commit()
    await db.refresh(found_user)
    return found_user


@router.delete(
    "/users/{user_id}",
    name="users:delete",
    summary="delete user by id",
    response_model=UserDB,
)
async def user_delete(user_id: int, request: Request) -> Optional[UserDB]:
    """Delete user by id from DB handler.

    Args:
        user_id: user id to be deleted
        request: incoming request

    Returns:
        deleted user from DB
    """
    db = request.app.state.db
    res = await db.execute(select(User).filter(User.id == user_id))
    found_user = res.scalar_one_or_none()
    if not found_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found",
        )
    await db.delete(found_user)
    await db.commit()
    return found_user
