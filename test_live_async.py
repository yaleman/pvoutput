""" test asyncio things """

import os
import json
import pytest

try:
    import aiohttp  # pylint: disable=unused-import
except ImportError as error_message:
    print(f"Failed to import aiohttp: {error_message}")
    pytest.fail()


# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio

# disabling this, needs to be done because of pytest
# pylint: disable=wrong-import-position

from pvoutput.asyncio import PVOutput


@pytest.fixture
def config():
    """configuration fixture"""
    if not os.path.exists(os.path.expanduser("~/.config/pvoutput.json")):
        print("Failed to find config file")
        pytest.skip()

    with open(
        os.path.expanduser("~/.config/pvoutput.json"), "r", encoding="utf8"
    ) as config_file:
        config_data = json.load(config_file)
    return config_data


# pylint: disable=redefined-outer-name
async def test_configured_async_getstatus(config):
    """tests the getstatus endpoint"""

    async with aiohttp.ClientSession() as session:
        pvo = PVOutput(
            apikey=config.get("apikey"),
            systemid=config.get("systemid"),
            donation_made=True,
            session=session,
        )

        result = await pvo.getstatus()
        assert result
        assert isinstance(result, dict)


async def test_check_rate_limit(config):
    """tests check rate limit with the getsystem endpoint"""

    async with aiohttp.ClientSession() as session:
        pvo = PVOutput(
            apikey=config.get("apikey"),
            systemid=config.get("systemid"),
            donation_made=True,
            session=session,
        )

        result = await pvo.check_rate_limit()
        assert result
        assert len(result) == 3


async def test_register_notification(config):
    """tests register notification"""

    async with aiohttp.ClientSession() as session:
        pvo = PVOutput(
            apikey=config.get("apikey"),
            systemid=config.get("systemid"),
            donation_made=True,
            session=session,
        )

        result = await pvo.register_notification(
            "my.application.id.async", "http://my.application.com/api/alert.php", 0
        )
        assert result
        assert result.status == 200
        assert await result.text() == "OK 200: Registered Notification"


async def test_deregister_notification(config):
    """tests deregister notification"""

    async with aiohttp.ClientSession() as session:
        pvo = PVOutput(
            apikey=config.get("apikey"),
            systemid=config.get("systemid"),
            donation_made=True,
            session=session,
        )

        result = await pvo.deregister_notification("my.application.id.async", 0)
        assert result
        assert result.status == 200
        assert await result.text() == "OK 200: Deregistered Notification"
