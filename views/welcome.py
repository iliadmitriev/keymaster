"""
Welcome views handlers.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root() -> dict:
    """Welcome message handler.

    Returns:
        dict with response
    """
    return {"message": "/docs"}
