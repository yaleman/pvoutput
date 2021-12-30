#!/usr/bin/env python3

""" test some things """

import os
import sys
import json
import pytest

try:
    import aiohttp #pylint: disable=unused-import
except ImportError as error_message:
    print(f"Failed to import aiohttp: {error_message}")
    pytest.fail()


# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio

from pvoutput.asyncio import PVOutput
from datetime import datetime, date,time

@pytest.fixture
def config():

    if not os.path.exists(os.path.expanduser("~/.config/pvoutput.json")):
        print("Failed to find config file")
        pytest.fail()

    with open(os.path.expanduser("~/.config/pvoutput.json"), 'r') as config_file:
        config = json.load(config_file)
    return config

async def test_configured_async_getstatus(config):
    """ tests the getstatus endpoint"""

    async with aiohttp.ClientSession() as session:
        pvo = PVOutput(apikey=config.get('apikey'), systemid=config.get('systemid'), donation_made=True, session=session)

        testdate = date.today()
        testtime = time(hour=20, minute=00)
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
