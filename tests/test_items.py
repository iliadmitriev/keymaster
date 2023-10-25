"""
Test item operations.
"""
from httpx import AsyncClient
import pytest

from schemas.items import Item


@pytest.mark.asyncio
async def test_items_get(get_client: AsyncClient):
    """Test getting an item.

    Args:
        get_client (AsyncClient): http test client.
    """
    response = await get_client.get("/items/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_items_post(item: Item, get_client: AsyncClient):
    """Test post of a new item.

    Args:
        item (Item): A new item object.
        get_client (AsyncClient): http test client.
    """
    response = await get_client.post("/items/", content=item.model_dump_json())
    assert response.status_code == 201
    assert response.json() == item.model_dump()
