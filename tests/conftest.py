"""
Pytest application configuration.

Args:
    - item
    - engine (database engine instance with applied migrations)
    - get_redis (redis connection instance)
    - get_app (main application instance)
    - get_client (a http client to work with application)
    - event_loop (event loop session override)
"""
import asyncio
import pathlib
import sys
from asyncio import AbstractEventLoop
from typing import List
from unittest import mock

import redis.asyncio as redis
from redis.asyncio.client import Redis
import pytest
import pytest_asyncio
from alembic.runtime.migration import RevisionStep, MigrationContext
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.future import Connection
from sqlalchemy.orm import sessionmaker

from alembic.config import Config
from alembic.operations import Operations
from alembic.runtime.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from models import Base, User
from schemas.items import Item

BASE_PATH = pathlib.Path(__file__).parent.parent
sys.path.append(str(BASE_PATH))


@pytest.fixture
def item() -> Item:
    """Fixture creates test item object."""
    return Item(
        name="Banana", price=2.99, tax=0.25, description="One pound of banana"
    )


def do_upgrade(revision: str, context: MigrationContext) -> List[RevisionStep]:
    """Apply revision to context.

    Args:
        revision: Current revision
        context: Revision apply context

    Returns:
        (List[RevisionStep])
    """
    alembic_script = context.script
    return alembic_script._upgrade_revs(
        alembic_script.get_heads(), revision
    )  # noqa


def do_run_migrations(
    connection: Connection, alembic_env: EnvironmentContext
) -> None:
    """Run migrations.

    Args:
        connection: database connection
        alembic_env: alembic environment

    Returns:
        None
    """
    alembic_env.configure(
        connection=connection,
        target_metadata=Base.metadata,
        fn=do_upgrade,
        render_as_batch=True,
    )
    migration_context = alembic_env.get_context()

    with migration_context.begin_transaction():
        with Operations.context(migration_context):
            migration_context.run_migrations()


async def async_migrate(
    engine: AsyncEngine, alembic_env: EnvironmentContext
) -> None:
    """Apply all migrations.

    Args:
        engine: Async Engine with connection
        alembic_env: alembic environment context

    Returns:
        None
    """
    async with engine.begin() as conn:
        await conn.run_sync(do_run_migrations, alembic_env)


async def migrate(engine: AsyncEngine, url: str) -> None:
    """Read alembic config and create environment context.

    Args:
        engine: async engine with connection
        url: url connection string

    Returns:
        None
    """
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "alembic")
    alembic_cfg.set_main_option("url", url)
    alembic_script = ScriptDirectory.from_config(alembic_cfg)
    alembic_env = EnvironmentContext(alembic_cfg, alembic_script)

    await async_migrate(engine, alembic_env)


async def disconnect(engine: AsyncEngine) -> None:
    """
    Disposes a database engine and destroy all of its connections.

    Args:
        engine: async sqlalchemy engine to be disposed

    Returns:
        None
    """
    await engine.dispose()


@pytest.fixture(scope="session")
def database_test_url() -> str:
    """
    Generate in memory sqlite db connect url for test purposes.

    Returns:
        url string for test database connection
    """
    return "sqlite+aiosqlite://?cache=shared"  # noqa


@pytest.fixture(scope="session")
def redis_test_url() -> str:
    """Generate test string for redis connection.

    Returns:
        url string for redis test database connection
    """
    return "redis://127.0.0.1:6379/0"


@pytest_asyncio.fixture(scope="session")
async def engine(database_test_url: str) -> AsyncEngine:
    """Create async engine and run alembic migrations on database.

    Returns:
        sqlalchemy async engine
    """
    url = database_test_url
    engine = create_async_engine(url, echo=False)
    await migrate(engine, url)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def get_redis(redis_test_url: str) -> Redis:
    """Create redis test connection pool with url connection string provided.

    Args:
        redis_test_url: url string

    Returns:
        Redis instance
    """
    return redis.from_url(redis_test_url)


@pytest_asyncio.fixture(scope="session")
async def get_app(
    engine: AsyncEngine,
    database_test_url: str,
    get_redis: Redis,
    redis_test_url: str,
) -> FastAPI:
    """Create FastApi test application with initialized database.

    Args:
        engine: async database engine instance
        database_test_url: db connection url
        get_redis: redis instance
        redis_test_url: redis connection instance

    Returns:
        FastAPI wsgi application instance
    """
    from config import connection

    connection.DATABASE_URL = database_test_url
    connection.REDIS_URL = redis_test_url
    with mock.patch("sqlalchemy.ext.asyncio.create_async_engine") as create_eng:
        # noinspection SpellCheckingInspection
        with mock.patch("db.redis.redis.from_url") as create_redis:
            create_redis.return_value = get_redis
            create_eng.return_value = engine
            from main import app

            async with LifespanManager(app):
                yield app


@pytest_asyncio.fixture()
async def get_client(get_app: FastAPI) -> AsyncClient:
    # noinspection SpellCheckingInspection
    """Create a custom async http client based on httpx AsyncClient.

    Args:
        get_app: FastAPI wsgi application instance

    Returns:
        httpx async client
    """
    async with AsyncClient(app=get_app, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture(scope="session")
async def add_some_user(engine: AsyncEngine) -> User:
    """Add test user to database and return it.

    Args:
        engine: async database engine is used for db connection session

    Returns:
        a model.User instance
    """
    async_session = sessionmaker(
        engine, expire_on_commit=False, autoflush=False, class_=AsyncSession
    )

    user_db = User(
        email="myuserwithid@example.com", password="password", is_active=True
    )
    async with async_session(bind=engine) as session:
        # add user
        session.add(user_db)
        await session.commit()
        await session.refresh(user_db)

    return user_db


@pytest.fixture(scope="session")
def event_loop() -> AbstractEventLoop:
    """Redefinition of base pytest-asyncio event_loop fixture.

    Redefinition of base pytest-asyncio event_loop fixture,
    which returns the same value but with scope session.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    yield loop
    loop.close()
