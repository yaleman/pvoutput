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

        # testdate = date.today()
        # testtime = time(hour=20, minute=00)
        # data = {
        #     'd' : testdate.strftime("%Y%m%d"),
        #     't' : testtime.strftime("%H:%M"),
        #     'v2' : 500, # power generation
        #     'v4' : 450, # power consumption
        #     'v5' : 23.5, # temperature
        #     'v6' : 234.0, # voltage
        #     'm1' : 'Testing', # custom message
        # }
        result = await pvo.getstatus()
        print(result)
        assert result

        print(await pvo.check_rate_limit())
