"""
Authentication methods module.

Methods:
    create_access_token: creates access token string
"""
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt

from config.auth import JWT_ALGORITHM, SECRET_KEY


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """Create access token string.

    Args:
        data: data dict to be added to access token
        expires_delta: token ttl, expire delta time in seconds

    Returns:
        string containing JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(seconds=5)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and verify JWT token.

    Args:
        token: input token.

    Returns:
        dict of decoded data (key, value)
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
