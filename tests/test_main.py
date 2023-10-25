import pytest


@pytest.mark.asyncio
async def test_read_main(get_client):
    response = await get_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "/docs"}
