from unittest import mock

import pytest
from starlette import status

from tests.test_redis import async_return


@pytest.mark.asyncio
async def test_view_health_check_200_ok(get_client, get_app):
    with mock.patch(
        "views.healthcheck.get_redis_key",
        mock.MagicMock(return_value=async_return(True)),
    ) as get_redis_mock:
        res = await get_client.get(get_app.url_path_for("health-check"))
    assert res.status_code == status.HTTP_200_OK
    get_redis_mock.assert_called_once()


@pytest.mark.asyncio
async def test_view_health_check_503_unavailable(get_client, get_app):
    with mock.patch(
        "sqlalchemy.ext.asyncio.AsyncSession.execute"
    ) as session_execute:
        session_execute.side_effect = ConnectionRefusedError()
        res = await get_client.get(get_app.url_path_for("health-check"))
        assert res.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


@pytest.mark.asyncio
async def test_view_health_check_500_internal_error(get_client, get_app):
    with pytest.raises(RuntimeError):
        with mock.patch(
            "sqlalchemy.ext.asyncio.AsyncSession.execute"
        ) as session_execute:
            session_execute.side_effect = RuntimeError()
            res = await get_client.get(get_app.url_path_for("health-check"))
            assert res.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
