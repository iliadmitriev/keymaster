"""
Test user schemas.
"""
from models import User
from schemas import UserCreate


def test_user_schema_dump_to_db_without_defaults():
    """Test user validation and schema conversion to db object."""
    user = UserCreate(
        email="fake@example.com", password="secret", is_superuser=False
    )
    user_db = User(**user.model_dump(exclude_unset=True))  # type: ignore

    assert user_db.email == "fake@example.com"
    assert user_db.password == "secret"
    assert user_db.email == user.email
    assert user_db.password == user.password
    assert user_db.is_superuser == user.is_superuser
    assert user_db.is_active is None
    assert user_db.confirmed is None
    assert user_db.last_login is None
    assert user_db.created is None


def test_user_schema_dump_to_db_with_defaults():
    """Test user schema validation with default values."""
    user = UserCreate(
        email="fake@example.com", password="secret", is_superuser=False
    )
    user_db = User(**user.model_dump())  # type: ignore

    assert user_db.email == "fake@example.com"
    assert user_db.password == "secret"
    assert user_db.email == user.email
    assert user_db.password == user.password
    assert user_db.is_superuser == user.is_superuser
    assert user_db.is_active
    assert not user_db.confirmed
    assert user_db.last_login is None
    assert user_db.created is None
