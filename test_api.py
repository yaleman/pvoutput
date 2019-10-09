import pytest
import pvoutput
from datetime import datetime, date, timedelta, time

def test_api_inputs():
    """ tests basic "this should fail" on API init """
    with pytest.raises(TypeError):
        foo = pvoutput.PVOutput(apikey=1234512345, systemid=1)
    with pytest.raises(TypeError):
        foo = pvoutput.PVOutput(apikey='helloworld', systemid='test')

def test_api_validation():
    """ tests a basic "this should clearly fail" validation """
    with pytest.raises(ValueError):
        pvoutput.PVOutput.validate_data(None, {}, pvoutput.ADDSTATUS_PARAMETERS)

def test_headers_gen():
    """ tests that PVOutput._headers() returns a valid dict """
    foo = pvoutput.PVOutput(apikey='helloworld', systemid=1)

    assert foo._headers() == {
            'X-Pvoutput-Apikey' : 'helloworld',
            'X-Pvoutput-SystemId' : '1',
        }

def test_api_validation_addstatus_shouldwork():
    foo = pvoutput.PVOutput(apikey='helloworld', systemid=1)

    data = {
        'd' : '20190515',
        't' : '1234',
        'v1' : 123,
    }
    assert foo.validate_data(data, pvoutput.ADDSTATUS_PARAMETERS) == True

def test_api_validation_types():
    foo = pvoutput.PVOutput(apikey='helloworld', systemid=1)

    data = {
        'd' : '20190515',
        't' : 1234,
        'v1' : '123',
    }
    with pytest.raises(TypeError):
        foo.validate_data(data, pvoutput.ADDSTATUS_PARAMETERS)

def test_delete_status_date_too_early():
    """ it should barf if you're setting it before yesterday """
    foo = pvoutput.PVOutput(apikey='helloworld', systemid=1)

    with pytest.raises(ValueError):
        foo.delete_status(date.today()-timedelta(days=2), testing=True)

def test_delete_status_date_too_late():
    """ it should barf if you're setting in the future """
    foo = pvoutput.PVOutput(apikey='helloworld', systemid=1)

    with pytest.raises(ValueError):
        foo.delete_status(date.today()+timedelta(days=2))

def test_delete_status_date_derp():
    """ it should barf if you're setting it to tomorrrow """
    foo = pvoutput.PVOutput(apikey='helloworld', systemid=1)

    with pytest.raises(ValueError):
        foo.delete_status(date_val=date.today() + timedelta(1))

def test_delete_status_invalid_time_val_type():
    foo = pvoutput.PVOutput(apikey='helloworld', systemid=1)

    with pytest.raises(ValueError):
        foo.delete_status(date_val=date.today(), time_val='lol')
        foo.delete_status(date_val=date.today(), time_val=123)
        foo.delete_status(date_val=date.today(), time_val=True)
        foo.delete_status(date_val=date.today(), time_val=time(hour=23,minute=59))

def test_donation_mode_keys():
    foo = pvoutput.PVOutput(apikey='helloworld', systemid=1)

    data = {
        'm1' : 'this will end badly',
        'v1' : 123
    }
    with pytest.raises(pvoutput.DonationRequired):
        foo.addstatus(data=data,testing=True)