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

## Python packages install

Runtime packages

```sh
pip install -r requirements.txt
```

Development packages

```sh
pip install -r requirements-dev.txt
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

## Start application

```shell
uvicorn main:app
```

Options

+ `--host` - set bind host (0.0.0.0 - to bind all interfaces, 127.0.0.1 - default)
+ `--port` - bind tcp port (default 8000)
+ `--reload` - start application with hot reload

# Usage

```
curl -v http://127.0.0.1:8000/health
```

## API documentation

1. Swagger Documentation http://127.0.0.1:8000/docs
2. ReDoc http://127.0.0.1:8000/redoc

