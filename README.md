# Auth microservice

This program is for educational purposes. It's created using FastAPI, pydantic and uvicorn.

# Install

## Application environment variables

for postgresql

```shell
DATABASE_DRIVER=postgresql+asyncpg
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=auth
DATABASE_USER=auth
DATABASE_PASSWORD=authsecret
```

for mysql

```shell
DATABASE_DRIVER=mysql+asyncmy
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=auth
DATABASE_USER=auth
DATABASE_PASSWORD=authsecret
```

add redis url to `.env`

```shell
REDIS_URL=redis://localhost:6379/0
```

## Run migrations

DB migrations located in `alembic` directory and based on alembic migrations

```shell
alembic upgrade head
```

# Tests

Tests located in `tests` directory and based on pytest

## run tests with coverage

```shell
pytest -v --cov=.
```

# Start Application

## Start application with hot reload

```shell
uvicorn main:app --reload 
```

# Usage

## API documentation

1. Swagger Documentation http://127.0.0.1:8000/docs
2. ReDoc http://127.0.0.1:8000/redoc

