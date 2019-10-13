from datetime import datetime, date, timedelta, time
import re

import pytest
import pvoutput
import requests_mock

# because we're testing, just grab everything.
URLMATCHER = re.compile('.*')

def test_api_inputs():
    """ tests basic "this should fail" on API init """
    with pytest.raises(TypeError):
        foo = pvoutput.PVOutput(apikey=1234512345, systemid=1)
    with pytest.raises(TypeError):
        foo = pvoutput.PVOutput(apikey="helloworld", systemid="test")


def test_api_validation():
    """ tests a basic "this should clearly fail" validation """
    with pytest.raises(ValueError):
        pvoutput.PVOutput.validate_data(None, {}, pvoutput.ADDSTATUS_PARAMETERS)


def test_headers_gen():
    """ tests that PVOutput._headers() returns a valid dict """
    foo = pvoutput.PVOutput(apikey="helloworld", systemid=1)

    assert foo._headers() == {
        "X-Pvoutput-Apikey": "helloworld",
        "X-Pvoutput-SystemId": "1",
    }


def test_api_validation_addstatus_shouldwork():
    foo = pvoutput.PVOutput(apikey="helloworld", systemid=1)

    data = {"d": "20190515", "t": "1234", "v1": 123}
    assert foo.validate_data(data, pvoutput.ADDSTATUS_PARAMETERS) == True


def test_api_validation_types():
    foo = pvoutput.PVOutput(apikey="helloworld", systemid=1)

    data = {"d": "20190515", "t": 1234, "v1": "123"}
    with pytest.raises(TypeError):
        foo.validate_data(data, pvoutput.ADDSTATUS_PARAMETERS)


def test_delete_status_date_too_early():
    """ it should barf if you're setting it before yesterday """
    foo = pvoutput.PVOutput(apikey="helloworld", systemid=1)

    with pytest.raises(ValueError):
        foo.delete_status(date.today() - timedelta(days=2))


def test_delete_status_date_too_late():
    """ it should barf if you're setting in the future """
    foo = pvoutput.PVOutput(apikey="helloworld", systemid=1)

    with pytest.raises(ValueError):
        foo.delete_status(date.today() + timedelta(days=2))


def test_delete_status_date_derp():
    """ it should barf if you're setting it to tomorrrow """
    foo = pvoutput.PVOutput(apikey="helloworld", systemid=1)

    with pytest.raises(ValueError):
        foo.delete_status(date_val=date.today() + timedelta(1))


def test_delete_status_invalid_time_val_type():
    foo = pvoutput.PVOutput(apikey="helloworld", systemid=1)

    with pytest.raises(ValueError):
        foo.delete_status(date_val=date.today(), time_val="lol")
        foo.delete_status(date_val=date.today(), time_val=123)
        foo.delete_status(date_val=date.today(), time_val=True)
        foo.delete_status(date_val=date.today(), time_val=time(hour=23, minute=59))

def test_donation_mode_keys():
    foo = pvoutput.PVOutput(apikey="helloworld", systemid=1)

    data = {"m1": "this will end badly", "v1": 123}
    with requests_mock.mock() as mock:
        mock.get(URLMATCHER, text="", status_code=200)
        with pytest.raises(pvoutput.DonationRequired):
            foo.addstatus(data=data)


def test_getstatus_donation_mode():
    foo = pvoutput.PVOutput(apikey="helloworld", systemid=1)
    mockdata_donation = (
        "20191012,23:00,15910,0,15973,724,NaN,NaN,239.4,33.000,NaN,NaN,NaN,NaN,NaN"
    )

    expecteddict = {
        "d": "20191012",
        "t": "23:00",
        "timestamp": datetime.strptime("20191012 23:00", "%Y%m%d %H:%M"),
        "v1": 15910,
        "v2": 0,
        "v3": 15973,
        "v4": 724,
        "v5": None,
        "v6": None,
        "normalised_output": 239.4,
        "v7": 33.000,
        "v8": None,
        "v9": None,
        "v10": None,
        "v11": None,
        "v12": None,
    }

    with requests_mock.mock() as mock:
        mock.get(
            url=URLMATCHER,
            text=mockdata_donation,
            status_code=200,
        )
        assert foo.getstatus() == expecteddict


def test_getstatus_donation_mode():
    foo = pvoutput.PVOutput(apikey="helloworld", systemid=1, donation_made=False)
    mockdata_donation = "20191012,23:00,15910,0,15973,724,NaN,NaN,239.4"

    expecteddict = {
        "d": "20191012",
        "t": "23:00",
        "timestamp": datetime.strptime("20191012 23:00", "%Y%m%d %H:%M"),
        "v1": 15910,
        "v2": 0,
        "v3": 15973,
        "v4": 724,
        "v5": None,
        "v6": None,
        "normalised_output": 239.4,
    }
    with requests_mock.mock() as mock:
        mock.get(
            url=URLMATCHER,
            text=mockdata_donation,
            status_code=200,
        )
        assert foo.getstatus() == expecteddict
