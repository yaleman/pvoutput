""" tests synchronous api things """
import datetime
import re

import pytest
import requests_mock

import pvoutput
import pvoutput.exceptions

# because we're testing, just grab everything.
URLMATCHER = re.compile(".*")

# used in test_datetime_fix
FAKE_TIME = datetime.datetime(2020, 9, 6, 12, 59, 00)


@pytest.fixture
def patch_datetime_now(monkeypatch):
    """patches datetime.now with a fake time
    based on this https://stackoverflow.com/questions/20503373/how-to-monkeypatch-pythons-datetime-datetime-now-with-py-test
    """

    class PatchedDateTime(datetime.datetime):
        """monkeypatched datetime"""

        @classmethod
        def now(cls, tz=None):  # pylint: disable=signature-differs
            return FAKE_TIME

    monkeypatch.setattr(datetime, "datetime", PatchedDateTime)


def test_patch_datetime(patch_datetime_now):
    """testing that the monkeypatching works"""
    assert datetime.datetime.now() == FAKE_TIME


def good_pvo_no_donation():
    """returns a valid PVOutput API object"""
    return pvoutput.PVOutput(apikey="helloworld", systemid=1, donation_made=False)


def good_pvo_with_donation():
    """returns a valid PVOutput API object"""
    return pvoutput.PVOutput(apikey="helloworld", systemid=1, donation_made=True)


def good_pvo():
    """returns a valid PVOutput API object that's not donating"""
    return good_pvo_no_donation()


def test_api_inputs():
    """tests basic "this should fail" on API init"""
    with pytest.raises(TypeError, match=r"apikey should be .*"):
        pvoutput.PVOutput(apikey=1234512345, systemid=1)
    with pytest.raises(TypeError, match=r"systemid should be .*"):
        pvoutput.PVOutput(apikey="helloworld", systemid="test")


def test_api_validation():
    """tests a basic "this should clearly fail" validation"""
    with pytest.raises(ValueError, match=r"one of .* MUST be set"):
        pvoutput.PVOutput.validate_data(None, {}, pvoutput.ADDSTATUS_PARAMETERS)


def test_validation_regexp_date():
    """tests the validator for format regexp date"""
    api = {
        "d": {
            "format": r"^(20\d{2})(\d{2})(\d{2})$",
        }
    }
    with pytest.raises(
        ValueError, match=r"key '.*', with value '.*' does not match '.*'"
    ):
        assert good_pvo_with_donation().validate_data({"d": "19000515"}, api)
    with pytest.raises(
        ValueError, match=r"key '.*', with value '.*' does not match '.*'"
    ):
        assert good_pvo_with_donation().validate_data({"d": "201905150"}, api)
    with pytest.raises(
        ValueError, match=r"key '.*', with value '.*' does not match '.*'"
    ):
        assert good_pvo_with_donation().validate_data({"d": "2019515"}, api)

    assert good_pvo_with_donation().validate_data({"d": "20190515"}, api)


def test_validation_regexp_time():
    """tests the validator for format regexp date"""
    api = {
        "t": {
            "format": r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$",
        }
    }
    with pytest.raises(
        ValueError, match=r"key '.*', with value '.*' does not match '.*'"
    ):
        assert good_pvo_with_donation().validate_data({"t": "0:00"}, api)
    with pytest.raises(
        ValueError, match=r"key '.*', with value '.*' does not match '.*'"
    ):
        assert good_pvo_with_donation().validate_data({"t": "00:0"}, api)
    with pytest.raises(
        ValueError, match=r"key '.*', with value '.*' does not match '.*'"
    ):
        assert good_pvo_with_donation().validate_data({"t": "24:00"}, api)
    with pytest.raises(
        ValueError, match=r"key '.*', with value '.*' does not match '.*'"
    ):
        assert good_pvo_with_donation().validate_data({"t": "23:60"}, api)

    assert good_pvo_with_donation().validate_data({"t": "00:00"}, api)
    assert good_pvo_with_donation().validate_data({"t": "12:59"}, api)
    assert good_pvo_with_donation().validate_data({"t": "23:59"}, api)


def test_api_validation_invalid_regexp():
    """tests the validator with an invalid regexp"""
    data = {"d": "20190515"}
    api = {
        "d": {
            "required": True,
            "description": "Date",
            "format": r"^([0-9]{8}$",
            "type": str,
            "donation_required": False,
        }
    }
    with pytest.raises(
        pvoutput.exceptions.InvalidRegexpError,
        match="Error for key '.*' with format '.*': .*",
    ):
        assert good_pvo_with_donation().validate_data(data, api)


def test_headers_gen(pvo=good_pvo()):
    """tests that PVOutput._headers() returns a valid dict"""
    # pylint: disable=protected-access
    assert pvo._headers() == {
        "X-Pvoutput-Apikey": "helloworld",
        "X-Pvoutput-SystemId": "1",
    }


def test_api_validation_addstatus_shouldwork():
    """tests the validator for addstatus()"""
    data = {"d": "20190515", "t": "12:34", "v1": 123}
    assert good_pvo_with_donation().validate_data(data, pvoutput.ADDSTATUS_PARAMETERS)


def test_api_validation_types(pvo=good_pvo()):
    """tests the type-based validation in addstatus on a fail"""
    data_failtime = {"d": "20190515", "t": 1234, "v1": "123"}
    data_faildate = {"d": 1, "t": "1234", "v1": "123"}
    with pytest.raises(
        TypeError,
        match=r"data\[.*\] type \(<class '.*'> is invalid - should be <class '.*'>\)",
    ):
        pvo.validate_data(data_failtime, pvoutput.ADDSTATUS_PARAMETERS)
    with pytest.raises(
        TypeError,
        match=r"data\[.*\] type \(<class '.*'> is invalid - should be <class '.*'>\)",
    ):
        pvo.validate_data(data_faildate, pvoutput.ADDSTATUS_PARAMETERS)


def test_delete_status_date_too_early(pvo=good_pvo()):
    """it should throw an error if you're deleting a status before yesterday"""
    # TODO: check if this is right for donation accounts
    with pytest.raises(
        ValueError, match=r"date_val can only be yesterday or today, you provided .*"
    ):
        pvo.delete_status(datetime.date.today() - datetime.timedelta(days=2))


def test_delete_status_date_too_late(pvo=good_pvo()):
    """it should throw an error if you're deleting a far-future status"""

    with pytest.raises(
        ValueError, match=r"date_val can only be yesterday or today, you provided .*"
    ):
        pvo.delete_status(datetime.date.today() + datetime.timedelta(days=2))


def test_delete_status_date_derp(pvo=good_pvo()):
    """it should barf if you're setting it to tomorrow"""
    with pytest.raises(
        ValueError, match=r"date_val can only be yesterday or today, you provided .*"
    ):
        pvo.delete_status(date_val=datetime.date.today() + datetime.timedelta(1))


def test_delete_status_invalid_time_val_type(pvo=good_pvo()):
    """if you're doing invalid time types, deletestatus() should fail"""
    with pytest.raises(TypeError):
        pvo.delete_status(date_val=datetime.date.today(), time_val="lol")
    with pytest.raises(TypeError):
        pvo.delete_status(date_val=datetime.date.today(), time_val=123)
    with pytest.raises(TypeError):
        pvo.delete_status(date_val=datetime.date.today(), time_val=True)


def test_delete_status_works(pvo=good_pvo()):
    """if you're doing invalid time types, deletestatus() should fail"""

    with requests_mock.mock() as mock:
        mock.post(URLMATCHER, text="Status Deleted", status_code=200)
        result = pvo.delete_status(
            date_val=datetime.date.today(), time_val=datetime.time(hour=23, minute=59)
        )
        assert result
        assert result.status_code == 200
        assert result.text == "Status Deleted"


def test_donation_made_keys():
    """test an addstatus on a non-donation account with a call that requires donations"""
    pvo = good_pvo_no_donation()
    data = {
        "m1": "this field requires donations",
        "v1": 123,
        "t": "23:59",
    }
    with requests_mock.mock() as mock:
        mock.get(URLMATCHER, text="", status_code=200)
        with pytest.raises(pvoutput.exceptions.DonationRequired):
            pvo.addstatus(data=data)


def test_addstatus_every_possible_time():
    """this'll test every possible time, because.. why not?"""
    pvo = good_pvo_with_donation()
    for hour in range(24):
        for minute in range(60):
            with requests_mock.mock() as mock:
                mock.post(URLMATCHER, text="", status_code=200)
                t_value = f"{hour:02}:{minute:02}"
                data = {
                    "t": t_value,
                    "v1": 54,
                }
                pvo.addstatus(data)


def test_getstatus_donation_made_true():
    """test getstatus in donation made"""
    mockdata_donation = (
        "20191012,23:00,15910,0,15973,724,NaN,NaN,239.4,33.000,NaN,NaN,NaN,NaN,NaN"
    )

    expecteddict = {
        "d": "20191012",
        "t": "23:00",
        "timestamp": datetime.datetime.strptime("20191012 23:00", "%Y%m%d %H:%M"),
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


def test_getstatus_donation_made_false():
    """test addstatus when you haven't made a donation, and you're not trying to do donation things"""
    mockdata_donation = "20191012,23:00,15910,0,15973,724,NaN,NaN,239.4"

    expecteddict = {
        "d": "20191012",
        "t": "23:00",
        "timestamp": datetime.datetime.strptime("20191012 23:00", "%Y%m%d %H:%M"),
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


def test_add_output():
    """tests the validator for addoutput()"""
    data = {"d": "20190515", "g": 123}
    pvo = good_pvo()
    with requests_mock.mock() as mock:
        mock.post(
            url=URLMATCHER,
            text="Added Output",
            status_code=200,
        )
        result = pvo.addoutput(data)
        assert result.status_code == 200
        assert result.text == "Added Output"


def test_add_output_float():
    """tests the validator for addoutput()"""
    data = {"d": "20190515", "g": 123.0}
    pvo = good_pvo_no_donation()

    with pytest.raises(
        TypeError,
        match=r"data\[g\].*<class 'float'> is invalid - should be <class 'int'>",
    ):
        pvo.validate_data(data, pvoutput.ADDOUTPUT_PARAMETERS)


def test_register_notification_url_maxlength():

    """tests a long-url entry fail into register notification"""
    pvo = pvoutput.PVOutput(apikey="helloworld", systemid=1, donation_made=False)
    with pytest.raises(ValueError):
        pvo.register_notification(appid="test", url="#" * 1000, alerttype=1)

    with pytest.raises(ValueError):
        with requests_mock.mock() as mock:
            mock.get(
                url=URLMATCHER,
                text="OK 200",
                status_code=200,
            )

            response = pvo.register_notification(
                appid="test",
                url=f"http://example.com/{'#'*1000}",
                alerttype=1,
            )
            assert response.status_code == 200


def test_register_notification_url_validresponse():
    """tests a valid entry into register notification"""
    pvo = pvoutput.PVOutput(apikey="helloworld", systemid=1, donation_made=False)
    with requests_mock.mock() as mock:
        mock.get(
            url=URLMATCHER,
            text="OK 200",
            status_code=200,
        )
        response = pvo.register_notification(
            appid="test", url="http://example.com", alerttype=1
        )
        assert response.status_code == 200


def test_register_notification_appid_maxlength(pvo=good_pvo()):
    """tests the max length of appids"""
    with requests_mock.mock() as mock:
        mock.get(
            url=URLMATCHER,
            text="OK 200",
            status_code=200,
        )
        with pytest.raises(ValueError):
            pvo.register_notification(appid="#" * 10, url="#" * 152, alerttype=1)
        with pytest.raises(ValueError):
            pvo.register_notification(appid="#" * 5, url="#" * 1000, alerttype=1)
        with pytest.raises(ValueError):
            pvo.register_notification(appid="#" * 1000, url="#" * 10, alerttype=1)
        with pytest.raises(ValueError):
            pvo.register_notification(appid="#" * 151, url="#" * 100, alerttype=1)

        response = pvo.register_notification(
            appid="test", url="http://example.com", alerttype=1
        )
        assert response.status_code == 200
        assert response.text == "OK 200"


def test_datetime_fix(patch_datetime_now):
    """tests issue https://github.com/yaleman/pvoutput/issues/53"""
    pvo = good_pvo()
    test_data = {
        "d": "20200905",
        "v1": 12345,
    }
    with requests_mock.mock() as mock:
        mock.post(
            url=URLMATCHER,
            text="OK 200",
            status_code=200,
        )
        response = pvo.addstatus(test_data)
        assert response.status_code == 200
