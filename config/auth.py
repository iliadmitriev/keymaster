"""
Application configuration file.
"""
from os import environ

SECRET_KEY = environ.get("SECRET_KEY", "test secret string for jwt")

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = 300
REFRESH_TOKEN_EXPIRE = 86400
