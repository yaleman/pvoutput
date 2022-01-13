""" test asyncio things """
import datetime
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


async def test_configured_async_addstatus(config):
    """test the addstatus endpoint"""

    testdate = datetime.date.today()
    testtime = datetime.time(hour=23, minute=45)
    data = {
        "d": testdate.strftime("%Y%m%d"),
        "t": testtime.strftime("%H:%M"),
        "v2": 500,  # power generation
        "v4": 450,  # power consumption
        "v5": 23.5,  # temperature
        "v6": 234.0,  # voltage
        "m1": "Testing",  # custom message
    }

    async with aiohttp.ClientSession() as session:
        pvo = PVOutput(
            apikey=config.get("apikey"),
            systemid=config.get("systemid"),
            donation_made=True,
            session=session,
        )
        addstatus_response = await pvo.addstatus(data)
        assert addstatus_response.status == 200
        assert await addstatus_response.text() == "OK 200: Added Status"


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


async def test_configured_deletestatus(config):
    """ test the deletestatus endpoint """
    testdate = datetime.date.today()
    testtime = datetime.time(hour=23, minute=45)

    async with aiohttp.ClientSession() as session:
        pvo = PVOutput(
            apikey=config.get("apikey"),
            systemid=config.get("systemid"),
            donation_made=True,
            session=session,
        )
        delete_result = await pvo.delete_status(testdate, testtime)
        assert delete_result
        assert delete_result.status == 200
        assert await delete_result.text() == "OK 200: Deleted Status"


async def test_configured_addoutput(config):
    """test the addoutput endpoint"""

    testdate = datetime.date.today()
    data = {
        "d": testdate.strftime("%Y%m%d"),
        "g": 500,  # Generated (Wh)
        "e": 450,  # Exported (Wh)
    }

    async with aiohttp.ClientSession() as session:
        pvo = PVOutput(
            apikey=config.get("apikey"),
            systemid=config.get("systemid"),
            donation_made=True,
            session=session,
        )
        addoutput_response = await pvo.addoutput(data)
        assert addoutput_response.status == 200
        assert await addoutput_response.text() == "OK 200: Added Output"


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
