import importlib
import os
from unittest import mock


def test_import_config():
    with mock.patch.dict(
        os.environ,
        {
            "DATABASE_NAME": "database",
            "DATABASE_USER": "user",
            "DATABASE_PASSWORD": "pass",
            "DATABASE_HOST": "host",
            "DATABASE_PORT": "5432",
            "DATABASE_DRIVER": "postgresql+asyncpg",
        },
    ):
        from config import connection

        importlib.reload(connection)
        assert connection.DATABASE_NAME == "database"
        assert connection.DATABASE_USER == "user"
        assert connection.DATABASE_PASSWORD == "pass"
        assert connection.DATABASE_HOST == "host"
        assert connection.DATABASE_PORT == "5432"
        assert connection.DATABASE_DRIVER == "postgresql+asyncpg"


def test_db_url():
    with mock.patch.dict(
        os.environ,
        {
            "DATABASE_NAME": "database",
            "DATABASE_USER": "user",
            "DATABASE_PASSWORD": "pass",
            "DATABASE_HOST": "host",
            "DATABASE_PORT": "5432",
            "DATABASE_DRIVER": "postgresql+asyncpg",
        },
    ):
        from config import connection

        importlib.reload(connection)
        assert (
            connection.DATABASE_URL
            == "postgresql+asyncpg://user:pass@host:5432/database"
        )


def test_redis_url():
    with mock.patch.dict(
        os.environ,
        {
            "REDIS_URL": "redis_secret_url",
        },
    ):
        from config import connection

        importlib.reload(connection)
        assert connection.REDIS_URL == "redis_secret_url"
