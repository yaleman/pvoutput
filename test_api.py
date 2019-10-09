import pytest
import pvoutput
from datetime import datetime

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
