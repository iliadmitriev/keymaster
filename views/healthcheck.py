"""
Healthcheck views module.
"""
import uuid

from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import InterfaceError
from starlette import status
from starlette.requests import Request

from db.redis import get_redis_key

router = APIRouter()


@router.get(
    "/health",
    name="health-check",
    summary="check application health status",
    description=(
        "checks connection with database"
        " performing simple query and responds if it's OK"
    ),
)
async def health_check(request: Request) -> dict:
    """Check connection to databases.

    Args:
        request: incoming request.

    Returns:
        dict or throws exception
    """
    db = request.app.state.db
    redis = request.app.state.redis
    try:
        res = await db.execute(text("select 1"))
        one = res.scalar()
        assert str(one) == "1"
        await get_redis_key(redis, uuid.uuid4().hex)
        return {"detail": "OK"}
    except (ConnectionRefusedError, InterfaceError, ConnectionError):
        raise HTTPException(
            detail="connection failed",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
