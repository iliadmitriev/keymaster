"""
Login schemas.
"""
from pydantic import BaseModel, EmailStr


class Register(BaseModel):
    """Register input schema."""

    email: EmailStr
    password: str


class Auth(Register):
    """Authentication input schema."""

    pass


class Token(BaseModel):
    """Token schema."""

    access_token: str
    refresh_token: str

    class Config:
        """Config for token schema."""

        orm_mode = True
