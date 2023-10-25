"""
Databases connections configuration.

- REDIS
- RDBMS
"""
from os import environ

DATABASE_DRIVER = environ.get("DATABASE_DRIVER")
DATABASE_NAME = environ.get("DATABASE_NAME")
DATABASE_USER = environ.get("DATABASE_USER")
DATABASE_PASSWORD = environ.get("DATABASE_PASSWORD")
DATABASE_HOST = environ.get("DATABASE_HOST")
DATABASE_PORT = environ.get("DATABASE_PORT")

DATABASE_URL = (
    f"{DATABASE_DRIVER}://{DATABASE_USER}:{DATABASE_PASSWORD}"
    f"@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
)


REDIS_URL = environ.get("REDIS_URL")
