import datetime

import pytest

from utils.auth import create_access_token, decode_token


@pytest.mark.asyncio
async def test_token_generate_from_data():
    expires_delta = datetime.timedelta(minutes=5)
    some_data = {"user": "username", "scope": ["group1", "group2"], "id": 999}
    token = create_access_token(some_data, expires_delta)
    payload = decode_token(token)
    assert some_data.items() <= payload.items()


@pytest.mark.asyncio
async def test_token_generate_from_data_without_expire():
    some_data = {"user": "username", "scope": ["group1", "group2"], "id": 999}
    token = create_access_token(some_data)
    payload = decode_token(token)
    assert some_data.items() <= payload.items()
