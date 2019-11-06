from datetime import datetime, date, timedelta, time
import re

import pytest
import pvoutput
import requests_mock

# because we're testing, just grab everything.
URLMATCHER = re.compile('.*')

def good_pvo_no_donation():
    """ returns a valid PVOutput API object """
    return pvoutput.PVOutput(apikey="helloworld", systemid=1, donation_made=False)

def good_pvo_with_donation():
    """ returns a valid PVOutput API object """
    return pvoutput.PVOutput(apikey="helloworld", systemid=1, donation_made=True)

def good_pvo():
    return good_pvo_no_donation()

def test_api_inputs():
    """ tests basic "this should fail" on API init """
    with pytest.raises(TypeError):
        pvoutput.PVOutput(apikey=1234512345, systemid=1)
    with pytest.raises(TypeError):
        pvoutput.PVOutput(apikey="helloworld", systemid="test")

def test_api_validation():
    """ tests a basic "this should clearly fail" validation """
    with pytest.raises(ValueError):
        pvoutput.PVOutput.validate_data(None, {}, pvoutput.ADDSTATUS_PARAMETERS)


def test_headers_gen(pvo=good_pvo()):
    """ tests that PVOutput._headers() returns a valid dict """
    assert pvo._headers() == {
        "X-Pvoutput-Apikey": "helloworld",
        "X-Pvoutput-SystemId": "1",
    }


def test_api_validation_addstatus_shouldwork():
    """ tests the validator for addstatus() """
    data = {"d": "20190515", "t": "1234", "v1": 123}
    assert good_pvo_with_donation().validate_data(data, pvoutput.ADDSTATUS_PARAMETERS) == True


def test_api_validation_types(pvo=good_pvo()):
    """ tests the type-based validation in addstatus on a fail """
    data_failtime = {"d": "20190515", "t": 1234, "v1": "123"}
    data_faildate = {"d": 1, "t": "1234", "v1": "123"}
    with pytest.raises(TypeError):
        pvo.validate_data(data_failtime, pvoutput.ADDSTATUS_PARAMETERS)
        pvo.validate_data(data_faildate, pvoutput.ADDSTATUS_PARAMETERS)


def test_delete_status_date_too_early(pvo=good_pvo()):
    """ it should throw an error if you're deleting a status before yesterday """
    # TODO: check if this is right for donation accounts
    with pytest.raises(ValueError):
        pvo.delete_status(date.today() - timedelta(days=2))


def test_delete_status_date_too_late(pvo=good_pvo()):
    """ it should throw an error if you're deleting a far-future status """

    with pytest.raises(ValueError):
        pvo.delete_status(date.today() + timedelta(days=2))


def test_delete_status_date_derp(pvo=good_pvo()):
    """ it should barf if you're setting it to tomorrrow """
    with pytest.raises(ValueError):
        pvo.delete_status(date_val=date.today() + timedelta(1))


def test_delete_status_invalid_time_val_type(pvo=good_pvo()):
    """ if you're doing invalid time types, deletestatus() should fail """
    with pytest.raises(ValueError):
        pvo.delete_status(date_val=date.today(), time_val="lol")
        pvo.delete_status(date_val=date.today(), time_val=123)
        pvo.delete_status(date_val=date.today(), time_val=True)
        pvo.delete_status(date_val=date.today(), time_val=time(hour=23, minute=59))

def test_donation_mode_keys():
    """ test an addstatus on a non-donation account with a call that requires donations """
    pvo = good_pvo_no_donation()
    data = {
        "m1": "this field requires donations", 
        "v1": 123,
        't' : "23:59",
        }
    with requests_mock.mock() as mock:
        mock.get(URLMATCHER, text="", status_code=200)
        with pytest.raises(pvoutput.DonationRequired):
            pvo.addstatus(data=data)

def test_addstatus_every_possible_time():
    """ this'll test every possible time, because.. why not? """
    pvo = good_pvo_with_donation()
    for h in range(24):
        for m in range(60):
            with requests_mock.mock() as mock:
                mock.post(URLMATCHER, text="", status_code=200)
                t = "%d.2:%d2" % (h, m)
                data = {
                    't' : t,
                    'v1' : 54,
                }
                pvo.addstatus(data)

def test_getstatus_donation_mode_true():
    """ test getstatus in donation mode """
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
        assert good_pvo_with_donation().getstatus() == expecteddict


def test_getstatus_donation_mode_false():
    """ test addstatus when you haven't made a donation, and you're not trying to do donation things """
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
        assert good_pvo_no_donation().getstatus() == expecteddict

def test_register_notification_url_maxlength():
    pvo = pvoutput.PVOutput(apikey="helloworld", systemid=1, donation_made=False)
    with pytest.raises(ValueError):
        pvo.register_notification(appid='test', url="#"*1000, alerttype=1)
    
    with pytest.raises(ValueError):
        with requests_mock.mock() as mock:
            mock.get(
                url=URLMATCHER,
                text="OK 200",
                status_code=200,
            )
    
            response = pvo.register_notification(
                appid='test', 
                url=f"http://example.com/{'#'*1000}", 
                alerttype=1,
                )
            assert response.status_code == 200
def test_register_notification_url_validresponse():    
    pvo = pvoutput.PVOutput(apikey="helloworld", systemid=1, donation_made=False)
    with requests_mock.mock() as mock:
        mock.get(
            url=URLMATCHER,
            text="OK 200",
            status_code=200,
        )
        response = pvo.register_notification(appid='test', url="http://example.com", alerttype=1)
        assert response.status_code == 200
        
def test_register_notification_appid_maxlength(pvo=good_pvo()):
    with pytest.raises(ValueError):
        with requests_mock.mock() as mock:
            mock.get(
                url=URLMATCHER,
                text="OK 200",
                status_code=200,
            )
            pvo.register_notification(appid='#'*10, url="#"*152, alerttype=1)
            pvo.register_notification(appid='#'*5, url="#"*1000, alerttype=1)
            pvo.register_notification(appid='#'*1000, url="#"*10, alerttype=1)
            pvo.register_notification(appid='#'*151, url="#"*100, alerttype=1)
    
    with requests_mock.mock() as mock:
        mock.get(
            url=URLMATCHER,
            text="OK 200",
            status_code=200,
        )
        response = pvo.register_notification(appid='test', url="http://example.com", alerttype=1)
        assert response.status_code == 200
