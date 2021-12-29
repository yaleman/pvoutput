#!/usr/bin/env python3

""" test some things """
import datetime
import sys
from datetime import date, time

import pytest

from src import pvoutput
from src.pvoutput.utils import get_apikey_systemid_from_config

try:
    import aiohttp  # pylint: disable=unused-import
except ImportError as error_message:
    print(f"Failed to import aiohttp: {error_message}")
    sys.exit(1)

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


# print("Testing delete_status for 20:00")
# print(pvo.delete_status(date_val=testdate, time_val=testtime).text)


@pytest.fixture
def api_sys():
    return get_apikey_systemid_from_config()


async def test_addstatus(api_sys):
    """ tests the addstatus endpoint"""

    async with aiohttp.ClientSession() as session:
        pvo = pvoutput.AsyncPVOutput(apikey=api_sys[0], systemid=api_sys[1], donation_made=True, session=session)

        testdate = date.today()
        testtime = time(hour=20, minute=00)
        data = {
            'd': testdate.strftime("%Y%m%d"),
            't': testtime.strftime("%H:%M"),
            'v2': 500,  # power generation
            'v4': 450,  # power consumption
            'v5': 23.5,  # temperature
            'v6': 234.0,  # voltage
            'm1': 'Testing',  # custom message
        }
        addstatus = await pvo.addstatus(data)
        assert addstatus is not None


async def test_getstatus(api_sys):
    """ tests the getstatus endpoint"""

    async with aiohttp.ClientSession() as session:
        pvo = pvoutput.AsyncPVOutput(apikey=api_sys[0], systemid=api_sys[1], donation_made=True, session=session)

        getstatus = (await pvo.getstatus())
        assert getstatus is not None


async def test_deletestatus(api_sys):
    """ tests the deletestatus endpoint"""

    async with aiohttp.ClientSession() as session:
        pvo = pvoutput.AsyncPVOutput(apikey=api_sys[0], systemid=api_sys[1], donation_made=True, session=session)

        testdate = date.today()
        testtime = time(hour=20, minute=00)
        delete_status = await pvo.delete_status(testdate, testtime)
        assert delete_status is not None
        assert delete_status.status == 200
        assert await delete_status.text() == 'OK 200: Deleted Status'


async def test_check_rate_limit(api_sys):
    """ tests the check rate limit with getsystem endpoint"""

    async with aiohttp.ClientSession() as session:
        pvo = pvoutput.AsyncPVOutput(apikey=api_sys[0], systemid=api_sys[1], donation_made=True, session=session)

        rate_limit = await pvo.check_rate_limit()
        assert rate_limit is not None
        assert len(rate_limit) == 3
        reset_datetime = datetime.datetime.fromtimestamp(int(rate_limit['X-Rate-Limit-Reset']), datetime.timezone.utc)
        remaining_timedelta = reset_datetime - datetime.datetime.now(datetime.timezone.utc)
        assert remaining_timedelta < datetime.timedelta(days=1)


async def test_register_notification(api_sys):
    async with aiohttp.ClientSession() as session:
        pvo = pvoutput.AsyncPVOutput(apikey=api_sys[0], systemid=api_sys[1], donation_made=True, session=session)
        appid = 'my.application.id.async'
        callback_url = 'http://my.application.com/api/alert.php'
        alert_type = 0
        register_response = await pvo.register_notification(appid, callback_url, alert_type)
        assert register_response.status == 200
        assert await register_response.text() == "OK 200: Registered Notification"


async def test_deregister_notification(api_sys):
    async with aiohttp.ClientSession() as session:
        pvo = pvoutput.AsyncPVOutput(apikey=api_sys[0], systemid=api_sys[1], donation_made=True, session=session)
        appid = 'my.application.id.async'
        alert_type = 0
        deregister_response = await pvo.deregister_notification(appid, alert_type)
        assert await deregister_response.text() == "OK 200: Deregistered Notification"
