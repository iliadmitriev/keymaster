"""
Pydantic schemas for users.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# base shared properties
class UserBase(BaseModel):
    """Base user schema."""

    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    confirmed: bool = False


# user create query
class UserCreate(UserBase):
    """User schema for create operation."""

    email: EmailStr
    password: str


# update user query
class UserUpdate(UserBase):
    """User schema for update operation."""

    password: Optional[str] = None


# output user
class UserOut(UserBase):
    """User schema for output operation."""

    id: Optional[int] = None
    created: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        """Config for user schema."""

        orm_mode = True


# user attributes stored in db
class UserDB(UserBase):
    """User schema for save into DB."""

    id: Optional[int] = None
    password: str
    created: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        """UserDB class config."""

        orm_mode = True
