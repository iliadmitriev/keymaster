import asyncio
import sys
from unittest import mock

import pytest

from db.redis import (
    app_dispose_redis,
    app_init_redis,
    get_redis_key,
    set_redis_key,
)


@pytest.mark.asyncio
async def test_init_redis():
    app = mock.MagicMock()
    from_url_mock = mock.Mock(return_value="test redis server")
    with mock.patch("db.redis.redis.from_url", from_url_mock):
        await app_init_redis(app)

    assert app.state.redis == "test redis server"

    from_url_mock.assert_called_once()


def async_return(result):
    """
    This func is used as a return value for using in await statements for python 3.7 hack
    In python 3.8 there is AsyncMock for that purpose.

    Usage:

        test = mock.MagicMock(return_value=async_return(some))
        res = await test()
        assert res == some

    :param result: returning result
    :return:
    """
    f = asyncio.Future()
    f.set_result(result)
    return f


@pytest.mark.asyncio
async def test_dispose_redis():
    app = mock.MagicMock()
    app.state.redis.close = mock.MagicMock(return_value=async_return(None))
    await app_dispose_redis(app)
    app.state.redis.close.assert_called_once()


@pytest.mark.skipif(
    sys.version_info < (3, 8), reason="requires python3.8 or higher"
)
@pytest.mark.asyncio
async def test_set_redis_key():
    redis = mock.MagicMock()
    redis.client.return_value.__aenter__.return_value.set.return_value = True
    res = await set_redis_key(redis=redis, key="test key", value="test value")
    redis.client.return_value.__aenter__.return_value.set.assert_called_once_with(
        "test key", "test value"
    )
    assert res


@pytest.mark.skipif(
    sys.version_info < (3, 8), reason="requires python3.8 or higher"
)
@pytest.mark.asyncio
async def test_set_redis_key_with_expire():
    redis = mock.MagicMock()
    redis.client.return_value.__aenter__.return_value.set.return_value = True
    res = await set_redis_key(
        redis=redis, key="test key", value="test value", expire=1000
    )
    redis.client.return_value.__aenter__.return_value.set.assert_called_once_with(
        "test key", "test value", ex=1000
    )
    assert res


@pytest.mark.skipif(
    sys.version_info < (3, 8), reason="requires python3.8 or higher"
)
@pytest.mark.asyncio
async def test_get_redis_key():
    redis = mock.MagicMock()
    redis.client.return_value.__aenter__.return_value.get.return_value = True
    res = await get_redis_key(redis=redis, key="test key")
    redis.client.return_value.__aenter__.return_value.get.assert_called_once_with(
        "test key"
    )
    assert res


class AMagicMock(mock.MagicMock):
    async def __aenter__(self):
        val = mock.MagicMock()
        f = asyncio.Future()
        f.set_result(True)
        val.set = mock.MagicMock(return_value=f)
        val.get = mock.MagicMock(return_value=f)
        return val

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.skipif(
    sys.version_info > (3, 8) or sys.version_info <= (3, 7),
    reason="requires python3.7",
)
@pytest.mark.asyncio
async def test_set_redis_key_py_3_7():
    redis = mock.MagicMock()
    redis.client.return_value = AMagicMock()
    res = await set_redis_key(redis=redis, key="test key", value="test value")
    assert res


@pytest.mark.skipif(
    sys.version_info > (3, 8) or sys.version_info <= (3, 7),
    reason="requires python3.7",
)
@pytest.mark.asyncio
async def test_set_redis_key_with_expire_py_3_7():
    redis = mock.MagicMock()
    redis.client.return_value = AMagicMock()
    res = await set_redis_key(
        redis=redis, key="test key", value="test value", expire=1000
    )
    assert res


@pytest.mark.skipif(
    sys.version_info > (3, 8) or sys.version_info <= (3, 7),
    reason="requires python3.7",
)
@pytest.mark.asyncio
async def test_set_redis_key_without_expire_py_3_7():
    redis = mock.MagicMock()
    redis.client.return_value = AMagicMock()
    res = await get_redis_key(redis=redis, key="test key")
    assert res
