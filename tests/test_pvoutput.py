#!/usr/bin/env python3
import datetime
from datetime import date, time

import pytest

from src import pvoutput
from src.pvoutput.utils import get_apikey_systemid_from_config


@pytest.fixture
def api_sys():
    return get_apikey_systemid_from_config()


@pytest.fixture
def pvo(api_sys):
    return pvoutput.PVOutput(apikey=api_sys[0], systemid=api_sys[1], donation_made=True)


def test_addstatus(pvo):
    """test the addstatus endpoint"""

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

    addstatus_response = pvo.addstatus(data)
    assert addstatus_response.text is not None


def test_getstatus(pvo):
    getstatus = pvo.getstatus()
    assert getstatus is not None


def test_deletestatus(pvo):
    testdate = date.today()
    testtime = time(hour=20, minute=00)
    delete_result = pvo.delete_status(testdate, testtime)
    assert delete_result
    assert delete_result.status_code == 200
    assert delete_result.text == 'OK 200: Deleted Status'


def test_check_rate_limit(pvo):
    """test the check rate limit with getsystem endpoint"""

    rate_limit = pvo.check_rate_limit()
    assert rate_limit is not None
    assert len(rate_limit) == 3
    reset_datetime = datetime.datetime.fromtimestamp(int(rate_limit['X-Rate-Limit-Reset']), datetime.timezone.utc)
    remaining_timedelta = reset_datetime - datetime.datetime.now(datetime.timezone.utc)
    assert remaining_timedelta < datetime.timedelta(days=1)


def test_register_notification(pvo):
    appid = 'my.application.id'
    callback_url = 'http://my.application.com/api/alert.php'
    alert_type = 0
    register_response = pvo.register_notification(appid, callback_url, alert_type)
    assert register_response.status_code == 200
    assert register_response.text == "OK 200: Registered Notification"


def test_deregister_notification(pvo):
    appid = 'my.application.id'
    alert_type = 0
    deregister_response = pvo.deregister_notification(appid, alert_type)
    assert deregister_response.status_code == 200
    assert deregister_response.text == "OK 200: Deregistered Notification"
