"""
Main start module.
"""
import uvicorn
from fastapi import FastAPI

from db.database import app_dispose_db, app_init_db
from db.redis import app_dispose_redis, app_init_redis
from views import healthcheck, items, login, users, welcome

DESCRIPTION = """
**API with HTTP Bearer authorization using JWT token**
"""


openapi_tags = [
    {
        "name": "login",
        "description": (
            "operations for users to register, login, logout or refresh token"
        ),
    },
    {
        "name": "users",
        "description": (
            "admin operations with users accounts: find, create, update, delete"
        ),
        "externalDocs": {
            "description": "Read more",
            "url": "https://iliadmitriev.github.io/auth-fapi/",
        },
    },
    {"name": "status", "description": "application status check methods"},
]

app = FastAPI(
    title="Auth-fAPI",
    version="0.0.1",
    description=DESCRIPTION,
    openapi_tags=openapi_tags,
    contact={
        "name": "Ilia Dmitriev",
        "url": "https://iliadmitriev.github.io/iliadmitriev/",
        "email": "ilia.dmitriev@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://github.com/iliadmitriev/auth-fapi/blob/master/LICENSE",
    },
)


@app.on_event("startup")
async def startup_event() -> None:
    """Startup events function."""
    await app_init_db(app)
    await app_init_redis(app)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Shutdown events function."""
    await app_dispose_db(app)
    await app_dispose_redis(app)


app.include_router(login.router, tags=["login"])
app.include_router(users.router, tags=["users"])
app.include_router(items.router, tags=["items"])
app.include_router(welcome.router)
app.include_router(healthcheck.router, tags=["status"])

if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(app, host="0.0.0.0", port=8000)
