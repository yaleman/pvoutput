"""tests parameters things"""

# import pytest
# import pvoutput


# def test_parameters_copying():
#     """checks if the copied values are different"""
#     assert pvoutput.ADDSTATUS_PARAMETERS["t"] != pvoutput.DELETESTATUS_PARAMETERS["t"]

from datetime import datetime

from pvoutput.parameters import ADDSTATUS_PARAMETERS
from pvoutput import PVOutput


def test_addstatus_default_date() -> None:
    """tests if the default date is set correctly"""
    assert ADDSTATUS_PARAMETERS["d"]["default"]() == datetime.today().strftime("%Y%m%d")  # type: ignore[index]

    test = PVOutput(apikey="helloworld", systemid=1, donation_made=False)
    assert test._validate_format(ADDSTATUS_PARAMETERS["d"]["format"], "d", ADDSTATUS_PARAMETERS["d"]["default"]()) is None  # type: ignore[index]
    from freezegun import freeze_time

    # freeze the time to a specific date that ISN'T the start date for testing
    @freeze_time("2037-01-11")
    def testit(test: PVOutput) -> None:
        # assert ADDSTATUS_PARAMETERS["d"]["default"]() == "20370111"
        test_data = {"v1": 1000, "t": "12:00"}
        assert test.validate_data(test_data, ADDSTATUS_PARAMETERS) is True
        print(test_data)
        assert test_data["d"] == "20370111"

    testit(test)
