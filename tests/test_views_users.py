"""
Test user views.
"""
import uuid

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status

from models import User
from schemas import UserCreate, UserUpdate
from utils.password import password_hash_ctx


@pytest.mark.asyncio
async def test_get_users_list(
    get_client: AsyncClient, get_app: FastAPI, add_some_user: User
):
    """Get list of users test.

    Args:
        get_client (AsyncClient): http test client.
        get_app (FastAPI): testing application.
        add_some_user (User): user added to database.
    """
    res = await get_client.get(get_app.url_path_for("users:get"))
    data = res.json()
    assert res.status_code == status.HTTP_200_OK
    user = next(item for item in data if item["id"] == add_some_user.id)
    assert user.get("id") == add_some_user.id
    assert user.get("email") == add_some_user.email
    assert user.get("is_active") == add_some_user.is_active
    assert user.get("confirmed") == add_some_user.confirmed
    assert user.get("is_superuser") == add_some_user.is_superuser


@pytest.mark.asyncio
async def test_get_user_by_id(
    get_client: AsyncClient, add_some_user: User, get_app: FastAPI
):
    """Get testing user from database by id.

    Args:
        get_client (AsyncClient): http test client.
        get_app (FastAPI): testing application.
        add_some_user (User): user added to database.
    """
    res = await get_client.get(
        get_app.url_path_for("users:get-by-id", user_id=str(add_some_user.id))
    )
    assert res.status_code == status.HTTP_200_OK
    assert {
        "confirmed": False,
        "email": "myuserwithid@example.com",
        "id": add_some_user.id,
        "is_active": True,
        "password": "password",
    }.items() <= res.json().items()


@pytest.mark.asyncio
async def test_get_user_by_id_not_exists(
    get_client: AsyncClient, get_app: FastAPI
):
    """Get non existing user from database by id.

    Args:
        get_client (AsyncClient): http test client.
        get_app (FastAPI): testing application.
    """
    res = await get_client.get(
        get_app.url_path_for("users:get-by-id", user_id="9999")
    )
    assert res.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_post_user_create_201_created(
    get_client: AsyncClient, get_app: FastAPI
):
    random_email = f"{uuid.uuid4().hex}@example.com"
    user = UserCreate(email=random_email, password="password")
    user_created = await create_new_user(get_app, get_client, user)
    assert not user_created.get("is_superuser")
    return user_created


async def create_new_user(
    get_app: FastAPI, get_client: AsyncClient, user: UserCreate
) -> dict:
    """
    Creates a new user using API post method

    :param: get_app: FastAPI application instance,
                    which is used to get url path for user creation endpoint
    :param: get_client: AsyncClient instance is performing http request
    :param: user: user to be posted to API method, created with UserCreate schema
    :return: dict with created user attributes
    """
    res = await get_client.post(
        get_app.url_path_for("users:post"), content=user.model_dump_json()
    )
    assert res.status_code == status.HTTP_201_CREATED
    assert not res.json().get("confirmed")
    assert res.json().get("is_active")
    assert res.json().get("email") == user.email
    assert password_hash_ctx.verify(user.password, res.json().get("password"))
    assert "created" in res.json()
    assert "last_login" in res.json()
    return res.json()


@pytest.mark.asyncio
async def test_post_user_create_400_bad_request(
    get_client: AsyncClient, get_app: FastAPI
):
    """Test create a new user with bad data.

    Args:
        get_client (AsyncClient): http test client.
        get_app (FastAPI): testing application.
    """
    random_email = "myuserwithid@example.com"
    user = UserCreate(email=random_email, password="password")
    res = await get_client.post(
        get_app.url_path_for("users:post"), content=user.model_dump_json()
    )
    assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "data",
    [
        {
            "confirmed": True,
            "is_active": False,
            "password": "new_password",
            "is_superuser": True,
            "email": f"{uuid.uuid4().hex}@example.com",
        },
        {
            "confirmed": True,
            "is_active": False,
            "is_superuser": True,
        },
    ],
)
async def test_put_user_update_200_ok(
    get_client: AsyncClient, get_app: FastAPI, data: dict
):
    """Test put users data to update user.

    Args:
        get_client (AsyncClient): http test client.
        get_app (FastAPI): testing application.
        data (dict): parametrized data.
    """
    user = await test_post_user_create_201_created(get_client, get_app)
    new_user = UserUpdate(**data)
    res = await get_client.put(
        get_app.url_path_for("users:put", user_id=user["id"]),
        content=new_user.model_dump_json(),
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.json().get("confirmed") == data.get("confirmed")
    assert res.json().get("is_active") == data.get("is_active")
    assert res.json().get("is_superuser") == data.get("is_superuser")
    assert res.json().get("id") == user["id"]
    assert res.json().get("email") == (data.get("email") or user["email"])
    if not data.get("password") is None:
        assert password_hash_ctx.verify(
            data.get("password"), res.json().get("password")  # type: ignore
        )
    assert "created" in res.json()
    assert "last_login" in res.json()


@pytest.mark.asyncio
async def test_put_user_update_404_not_found(
    get_client: AsyncClient, get_app: FastAPI
):
    """Try ti update non-existing user.

    Args:
        get_client (AsyncClient): http test client.
        get_app (FastAPI): testing application.
    """
    user = await test_post_user_create_201_created(get_client, get_app)
    new_user = UserUpdate(**user)
    res = await get_client.put(
        get_app.url_path_for("users:put", user_id="9999"),
        content=new_user.model_dump_json(),
    )
    assert res.status_code == status.HTTP_404_NOT_FOUND
    assert res.json() == {"detail": "User with id '9999' not found"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "data",
    [
        {"email": f"{uuid.uuid4().hex}@example.com"},
        {
            "confirmed": True,
        },
        {
            "password": "absolutely_new_pass",
        },
    ],
)
async def test_patch_user_update_200_ok(
    get_client: AsyncClient, get_app: FastAPI, data: dict
):
    """Test partial update uses data with patch.

    Args:
        get_client (AsyncClient): http test client.
        get_app (FastAPI): testing application.
        data (dict): parametrized data.
    """
    user = await test_post_user_create_201_created(get_client, get_app)
    new_user = UserUpdate(**data)
    res = await get_client.patch(
        get_app.url_path_for("users:patch", user_id=user["id"]),
        content=new_user.model_dump_json(
            exclude_defaults=True, exclude_unset=True
        ),
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.json().get("id") == user["id"]
    assert res.json().get("confirmed") == (
        data.get("confirmed") or user["confirmed"]
    )
    assert res.json().get("is_active") == (
        data.get("is_active") or user["is_active"]
    )
    assert res.json().get("is_superuser") == (
        data.get("is_superuser") or user["is_superuser"]
    )
    if not data.get("password") is None:
        assert password_hash_ctx.verify(
            data.get("password"), res.json().get("password")  # type: ignore
        )
    assert res.json().get("email") == (data.get("email") or user["email"])
    assert "last_login" in res.json()
    assert "created" in res.json()


@pytest.mark.asyncio
async def test_patch_user_update_404_not_found(
    get_client: AsyncClient, get_app: FastAPI
):
    """Test partial user data change for non-existing user.

    Args:
        get_client (AsyncClient): http test client.
        get_app (FastAPI): testing application.
    """
    user = await test_post_user_create_201_created(get_client, get_app)
    new_user = UserUpdate(**user)
    res = await get_client.patch(
        get_app.url_path_for("users:patch", user_id="9999"),
        content=new_user.model_dump_json(),
    )
    assert res.status_code == status.HTTP_404_NOT_FOUND
    assert res.json() == {"detail": "User with id '9999' not found"}


@pytest.mark.asyncio
async def test_delete_user_200_ok(get_client: AsyncClient, get_app: FastAPI):
    """Test successful delete of user.

    Args:
        get_client (AsyncClient): http test client.
        get_app (FastAPI): testing application.
    """
    user = await test_post_user_create_201_created(get_client, get_app)
    res = await get_client.delete(
        get_app.url_path_for("users:delete", user_id=user["id"]),
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.json().get("id") == user["id"]
    assert res.json().get("confirmed") == user["confirmed"]
    assert res.json().get("is_active") == user["is_active"]
    assert res.json().get("is_superuser") == user["is_superuser"]
    assert res.json().get("password") == user["password"]
    assert res.json().get("email") == user["email"]
    assert "last_login" in res.json()
    assert "created" in res.json()


@pytest.mark.asyncio
async def test_delete_user_404_not_found(
    get_client: AsyncClient, get_app: FastAPI
):
    """Test deleting of non-existing user.

    Args:
        get_client (AsyncClient): http test client.
        get_app (FastAPI): testing application.
    """
    res = await get_client.delete(
        get_app.url_path_for("users:patch", user_id="9999")
    )
    assert res.status_code == status.HTTP_404_NOT_FOUND
    assert res.json() == {"detail": "User with id '9999' not found"}
