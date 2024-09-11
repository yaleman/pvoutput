"""test sync things"""

import datetime
import json
import os
from typing import Any, Dict

import pytest

from pvoutput import PVOutput


@pytest.fixture
def config() -> Dict[str, Any]:
    """configuration fixture"""
    if not os.path.exists(os.path.expanduser("~/.config/pvoutput.json")):
        print("Failed to find config file")
        pytest.skip()

    with open(os.path.expanduser("~/.config/pvoutput.json"), "r", encoding="utf8") as config_file:
        config_data: Dict[str, Any] = json.load(config_file)
    return config_data


@pytest.fixture
def pvo(config: Dict[str, Any]) -> PVOutput:
    """fixture for testing"""
    return PVOutput(
        apikey=config["apikey"],
        systemid=config["systemid"],
        donation_made=True,
    )


def test_check_rate_limit(pvo: PVOutput) -> None:
    """tests check rate limit with the getsystem endpoint"""
    result = pvo.check_rate_limit()
    assert result
    assert len(result) == 3


def test_addstatus(pvo: PVOutput) -> None:
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

    addstatus_response = pvo.addstatus(data)
    assert addstatus_response.status_code == 200
    assert addstatus_response.text == "OK 200: Added Status"


def test_getstatus(pvo: PVOutput) -> None:
    """tests the getstatus endpoint"""
    result = pvo.getstatus()
    assert result
    assert isinstance(result, dict)


def test_deletestatus(pvo: PVOutput) -> None:
    """tests deletestatus"""
    testdate = datetime.date.today()
    testtime = datetime.time(hour=23, minute=45)
    delete_result = pvo.delete_status(testdate, testtime)
    assert delete_result
    assert delete_result.status_code == 200
    assert delete_result.text == "OK 200: Deleted Status"


def test_addoutput(pvo: PVOutput) -> None:
    """test the addoutput endpoint"""

    testdate = datetime.date.today()
    data = {
        "d": testdate.strftime("%Y%m%d"),
        "g": 500,  # Generated (Wh)
        "e": 450,  # Exported (Wh)
    }

    addoutput_response = pvo.addoutput(data)
    assert addoutput_response.status_code == 200
    assert addoutput_response.text == "OK 200: Added Output"


def test_register_notification(pvo: PVOutput) -> None:
    """tests register notification"""
    result = pvo.register_notification("my.application.id", "http://my.application.com/api/alert.php", 0)
    assert result
    assert result.status_code == 200
    assert result.text == "OK 200: Registered Notification"


def test_deregister_notification(pvo: PVOutput) -> None:
    """tests deregister notification"""
    result = pvo.deregister_notification("my.application.id", 0)
    assert result
    assert result.status_code == 200
    assert result.text == "OK 200: Deregistered Notification"
