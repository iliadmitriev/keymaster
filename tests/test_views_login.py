"""
Module for login view tests.
"""
import uuid
from unittest import mock

import pytest
from sqlalchemy.future import select
from starlette import status

from config.auth import REFRESH_TOKEN_EXPIRE
from models import User
from schemas import Auth, Register, UserCreate
from tests.test_redis import async_return
from tests.test_views_users import create_new_user
from utils.auth import decode_token
from utils.password import password_hash_ctx


@pytest.mark.asyncio
async def test_login_register_success(get_client, get_app):
    """Test login success.

    Args:
        get_client (_type_): http test client.
        get_app (_type_): http application.
    """
    email = f"{uuid.uuid4().hex}@example.com"
    password = uuid.uuid4().hex
    register = Register(email=email, password=password)
    data = register.model_dump_json()
    res = await get_client.post(
        get_app.url_path_for("login:register"), content=data
    )
    assert res.status_code == status.HTTP_200_OK
    db = get_app.state.db
    res = await db.execute(select(User).filter(User.email == email))
    found_user = res.scalar_one_or_none()
    assert found_user
    assert password_hash_ctx.verify(password, found_user.password)


@pytest.mark.asyncio
async def test_login_register_fail_exists(get_client, get_app, add_some_user):
    """Test login with negative outcome.

    Args:
        get_client (_type_): http test client.
        get_app (_type_): http application.
        add_some_user (_type_): fixture user.
    """
    register_exists = Register(
        email=add_some_user.email, password=uuid.uuid4().hex
    )
    res = await get_client.post(
        get_app.url_path_for("login:register"),
        content=register_exists.model_dump_json(),
    )
    assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "data",
    [
        {
            "email": f"{uuid.uuid4().hex}@example.com",
            "password": "new_password",
            "is_superuser": False,
        },
        {
            "email": f"{uuid.uuid4().hex}@example.com",
            "password": "new_password",
            "is_superuser": True,
        },
    ],
)
async def test_login_auth_success(get_client, get_app, data):
    """Test login with positive outcome.

    Args:
        get_client (_type_): http test client.
        get_app (_type_): http application.
        data (_type_): parametrized data.
    """
    user = UserCreate(
        email=data.get("email"),
        password=data.get("password"),
        is_superuser=data.get("is_superuser"),
    )
    created_user = await create_new_user(get_app, get_client, user)
    auth_user = Auth(**created_user)
    auth_user.password = data.get("password")
    with mock.patch(
        "views.login.set_redis_key",
        mock.MagicMock(return_value=async_return(True)),
    ) as set_redis_mock:
        res = await get_client.post(
            get_app.url_path_for("login:auth"),
            content=auth_user.model_dump_json(),
        )
    assert res.status_code == status.HTTP_200_OK
    assert "access_token" in res.json()
    assert "refresh_token" in res.json()
    assert (
        len(res.json().get("access_token").split(".")) == 3
    ), "JWT token should have 3 segments"
    assert (
        len(res.json().get("refresh_token").split(".")) == 3
    ), "JWT token should have 3 segments"
    access_payload = decode_token(res.json().get("access_token"))
    refresh_payload = decode_token(res.json().get("refresh_token"))
    assert "exp" in access_payload
    assert "jti" in access_payload
    assert access_payload.get("email") == data.get("email")
    assert access_payload.get("id") == created_user.get("id")
    assert "exp" in refresh_payload
    assert "exp" in access_payload
    assert refresh_payload.get("email") == data.get("email")
    assert refresh_payload.get("id") == created_user.get("id")
    set_redis_mock.assert_called_once_with(
        get_app.state.redis,
        res.json().get("refresh_token"),
        "1",
        REFRESH_TOKEN_EXPIRE,
    )


@pytest.mark.asyncio
async def test_login_auth_not_found(get_client, get_app):
    """Test login auth when user not found.

    Args:
        get_client (_type_): http test client.
        get_app (_type_): http application.
    """
    email = f"{uuid.uuid4().hex}@example.com"
    password = "new_password"
    user = UserCreate(email=email, password=password)
    with mock.patch(
        "views.login.set_redis_key",
        mock.MagicMock(return_value=async_return(True)),
    ) as set_redis_mock:
        res = await get_client.post(
            get_app.url_path_for("login:auth"), content=user.model_dump_json()
        )
    assert res.status_code == status.HTTP_404_NOT_FOUND
    set_redis_mock.assert_not_called()


@pytest.mark.asyncio
async def test_login_auth_password_not_match(get_client, get_app):
    """Test login auth when passwords don't match.

    Args:
        get_client (_type_): http test client.
        get_app (_type_): http application.
    """
    email = f"{uuid.uuid4().hex}@example.com"
    password = "new_password_not_match"
    user = UserCreate(email=email, password=password)
    created_user = await create_new_user(get_app, get_client, user)
    auth_user = Auth(**created_user)
    with mock.patch(
        "views.login.set_redis_key",
        mock.MagicMock(return_value=async_return(True)),
    ) as set_redis_mock:
        res = await get_client.post(
            get_app.url_path_for("login:auth"),
            content=auth_user.model_dump_json(),
        )
    assert res.status_code == status.HTTP_404_NOT_FOUND
    set_redis_mock.assert_not_called()
