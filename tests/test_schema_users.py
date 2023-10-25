"""
Test user schemas.
"""
import pytest
from pydantic import ValidationError

from schemas import UserBase, UserCreate, UserDB, UserUpdate


def test_user_base():
    """Test user base schema."""
    user = UserBase(email="test@example.com")
    assert user.email == "test@example.com"
    assert user.is_active
    assert not user.is_superuser
    assert not user.confirmed
    assert user.model_dump(exclude_unset=True) == {"email": "test@example.com"}
    assert user.model_dump() == {
        "email": "test@example.com",
        "is_active": True,
        "is_superuser": False,
        "confirmed": False,
    }


def test_user_base_email_empty():
    """Test user schema with empty email."""
    user = UserBase()
    assert user.email is None
    assert user.model_dump(exclude_unset=True) == {}
    assert user.model_dump() == {
        "email": None,
        "is_active": True,
        "is_superuser": False,
        "confirmed": False,
    }


def test_user_base_email_not_valid():
    """Test user schema with invalid email raises a validation error."""
    with pytest.raises(ValidationError):
        UserBase(email="not_valid_email")


def test_user_create():
    """Test create user schema."""
    user = UserCreate(email="test@example.com", password="password")
    assert user.email == "test@example.com"
    assert user.password == "password"
    assert user.is_active
    assert not user.is_superuser
    assert not user.confirmed


def test_user_create_password_empty():
    """Test create user schema with empty password."""
    with pytest.raises(ValidationError):
        UserCreate(user="test@example.com")  # type: ignore


def test_user_update():
    """Test user update schema."""
    user = UserUpdate(email="test@example.com")
    assert user.email == "test@example.com"
    assert user.password is None
    assert user.is_active
    assert not user.is_superuser
    assert not user.confirmed


def test_user_update_with_password():
    """Test user update with password set."""
    user = UserUpdate(email="test@example.com", password="password")
    assert user.email == "test@example.com"
    assert user.password == "password"
    assert user.is_active
    assert not user.is_superuser
    assert not user.confirmed


def test_user_db():
    """Test user schema with orm mode."""
    user = UserDB(email="test@example.com", password="secret")
    assert user.email == "test@example.com"
    assert user.password == "secret"
    assert user.is_active
    assert not user.is_superuser
    assert not user.confirmed
    assert user.id is None
    assert user.last_login is None
    assert user.created is None
