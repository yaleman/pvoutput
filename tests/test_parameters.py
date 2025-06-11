"""tests parameters things"""

import copy
from datetime import datetime
from typing import Any, Dict
import pytest
from pvoutput import PVOutput
from pvoutput.base import PVOutputBase
from pvoutput.parameters import ADDSTATUS_PARAMETERS


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


def test_parameters_copying() -> None:
    """checks if the copied values are different"""
    # This test is commented out but kept for reference
    # assert pvoutput.ADDSTATUS_PARAMETERS["t"] != pvoutput.DELETESTATUS_PARAMETERS["t"]
    pass


class TestC1V3Validation:
    """Test cases for c1 flag and v3 validation logic"""

    def setup_method(self) -> None:
        """Setup test fixtures"""
        self.pvo_base = PVOutputBase(apikey="test", systemid=123)

    def test_v3_exceeds_maxval_without_c1_flag_should_fail(self) -> None:
        """Test that v3 values > 200000 fail validation when c1 is not set"""
        data = {"v3": 250000}  # Exceeds maxval of 200000

        with pytest.raises(ValueError, match="v3 cannot be higher than 200000"):
            self.pvo_base.validate_data(data, ADDSTATUS_PARAMETERS)

    def test_v3_exceeds_maxval_with_c1_flag_should_pass(self) -> None:
        """Test that v3 values > 200000 pass validation when c1 is set"""
        data = {"v3": 250000, "c1": 1}  # c1 flag set, should bypass maxval check

        # Should not raise an exception
        result = self.pvo_base.validate_data(data, ADDSTATUS_PARAMETERS)
        assert result is True

    def test_v3_exceeds_maxval_with_c1_flag_value_2_should_pass(self) -> None:
        """Test that v3 values > 200000 pass validation when c1=2"""
        data = {"v3": 300000, "c1": 2}  # c1=2, should bypass maxval check

        result = self.pvo_base.validate_data(data, ADDSTATUS_PARAMETERS)
        assert result is True

    def test_v3_exceeds_maxval_with_c1_flag_value_3_should_pass(self) -> None:
        """Test that v3 values > 200000 pass validation when c1=3"""
        data = {"v3": 500000, "c1": 3}  # c1=3, should bypass maxval check

        result = self.pvo_base.validate_data(data, ADDSTATUS_PARAMETERS)
        assert result is True

    def test_v3_within_maxval_without_c1_flag_should_pass(self) -> None:
        """Test that v3 values <= 200000 pass validation without c1 flag"""
        data = {"v3": 150000}  # Within maxval limit

        result = self.pvo_base.validate_data(data, ADDSTATUS_PARAMETERS)
        assert result is True

    def test_v3_within_maxval_with_c1_flag_should_pass(self) -> None:
        """Test that v3 values <= 200000 pass validation with c1 flag"""
        data = {"v3": 150000, "c1": 1}  # Within limit, c1 set

        result = self.pvo_base.validate_data(data, ADDSTATUS_PARAMETERS)
        assert result is True

    def test_other_fields_maxval_validation_unaffected_by_c1(self) -> None:
        """Test that c1 flag doesn't affect maxval validation of other fields"""
        # Create a modified parameter set with maxval for testing
        test_params: Dict[str, Any] = copy.deepcopy(ADDSTATUS_PARAMETERS)
        test_params["v2"] = {"maxval": 1000, "type": int}

        data = {"v2": 1500, "c1": 1}  # v2 exceeds maxval, c1 set

        with pytest.raises(ValueError, match="v2 cannot be higher than 1000"):
            self.pvo_base.validate_data(data, test_params)

    def test_v3_minval_validation_still_applies_with_c1(self) -> None:
        """Test that minval validation for v3 still applies even when c1 is set"""
        # Create a deep copy of parameters and modify v3 to have minval
        test_params: Dict[str, Any] = copy.deepcopy(ADDSTATUS_PARAMETERS)
        test_params["v3"]["minval"] = 0

        data = {"v3": -100, "c1": 1}  # Negative value, c1 set

        with pytest.raises(ValueError, match="v3 cannot be lower than 0"):
            self.pvo_base.validate_data(data, test_params)

    def test_c1_flag_zero_does_not_bypass_v3_maxval(self) -> None:
        """Test that c1=0 (if somehow passed) doesn't bypass v3 maxval validation"""
        data = {"v3": 250000, "c1": 0}  # c1=0 is not a valid flag value

        # This should fail because c1=0 is not considered "set" for our logic
        # Note: This would also fail format validation, but testing the maxval logic specifically
        with pytest.raises(ValueError):
            self.pvo_base.validate_data(data, ADDSTATUS_PARAMETERS)
