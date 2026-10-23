"""base class for pvoutput"""

import re
from datetime import datetime, time
from math import floor
from typing import Any

from .exceptions import DonationRequired, InvalidRegexpError


def round_to_base(number: float, base: float) -> float:
    """rounds down to a specific base number
    based on answer in https://stackoverflow.com/a/2272174/188774
    """
    return base * round(floor(number / base))


class PVOutputBase:
    """base class for the PVOutput API"""

    def __init__(
        self,
        apikey: str,
        systemid: int,
        donation_made: bool = False,
        stats_period: int = 5,
    ) -> None:
        if not isinstance(systemid, int):
            raise TypeError("systemid should be int")
        if not isinstance(apikey, str):
            raise TypeError("apikey should be str")
        self.apikey = apikey
        self.systemid = systemid
        self.donation_made = donation_made
        self.stats_period = stats_period

    def _headers(self) -> dict[str, str]:
        """Relevant documentation: https://pvoutput.org/help/api_specification.html#http-headers

        :return: headers for calls to the API
        :rtype: dict
        """
        headers = {
            "X-Pvoutput-Apikey": self.apikey,
            "X-Pvoutput-SystemId": str(self.systemid),
        }
        return headers

    def get_time_by_base(self) -> str:
        """rounds the current time to the base specified (ie, to 15 minutes or 5 minutes etc)"""
        now = datetime.now()
        hour = int(now.strftime("%H"))
        # round the minute to the current stats period
        minute = int(round_to_base(now.minute, self.stats_period))
        return time(hour=hour, minute=minute).strftime("%H:%M")

    @classmethod
    def _validate_format(
        cls,
        format_string: str,
        key: str,
        value: Any,
    ) -> None:
        """handles the regular expression format checks"""
        try:
            match = re.match(str(format_string), str(value))
            if match is None:
                raise ValueError(f"key '{key}', with value '{value}' does not match '{format_string!r}'")
        except re.error as error:
            raise InvalidRegexpError("Error for key '{key}' with format '{format_string!r}': {error}") from error

    # pylint: disable=too-many-branches
    def validate_data(self, data: dict[str, Any], apiset: dict[str, Any]) -> bool:
        """Does a super-simple validation based on the api def raises errors if it's wrong, returns True if it's OK

        This'll only raise an error on the first error it finds

        :param data: the data to validate.
        :type data: dict

        :param apiset: A set of validation rules, eg: pvoutput.ADDSTATUS_PARAMETERS
        :type apiset: dict

        :raises TypeError: if the type testing fails.
        :raises ValueError: if you're trying to pass an invalid value.
        :raises pvoutput.InvalidRegexpError: if value does not match the regexp in format.
        """
        # if you set a 'required_oneof' key in apiset, validation will require at least one of those keys to be set
        if "required_oneof" in apiset and (len([key for key in data if key in apiset["required_oneof"]["keys"]]) == 0):
            raise ValueError(f"one of {','.join(apiset['required_oneof']['keys'])} MUST be set")
        for key, value in apiset.items():
            # check that that required values are set
            if value.get("required", False) and key not in data:
                if "default" in value:
                    if callable(value["default"]):
                        # if the default is a callable, call it to get the value
                        data[key] = value["default"]()
                    else:
                        # set a default value
                        data[key] = value["default"]
                else:
                    raise ValueError(f"key {key} required in data")

            # check maxlen
            if "maxlen" in value and key in data and len(data[key]) > value["maxlen"]:
                raise ValueError(f"Value too long for key {key} {len(data[key])}>{value['maxlen']}")

            # check the value is in the set of valid choices
            if "choices" in value and key in data and data[key] not in value["choices"]:
                raise ValueError(f"Invalid value for key {key}: '{data[key]}', should be in {value['choices']} ")

        # check there's no extra fields in the data
        for key, value in data.items():
            if key not in apiset:
                raise ValueError(f"key {key} isn't valid in the API spec")

            if apiset[key].get("type") and not isinstance(value, apiset[key]["type"]) and value is not None:
                raise TypeError(f"data[{key}] type ({type(value)} is invalid - should be {apiset[key]['type']!s})")

        for key, value in data.items():
            if "format" in apiset[key]:
                self._validate_format(apiset[key]["format"], key, value)
            # can run additional functions over the data
            if "additional_validators" in apiset[key]:
                for validator in apiset[key]["additional_validators"]:
                    validator(value)

            # TODO: 'd' can't be more than 14 days ago, if a donator, goes out to 90
            # check if donation_made == True and age of thing
            # if self.donation_made:
            #     # check if more than 90 days ago
            # else:
            #     # check if more than 14 days ago

            # check for donation-only keys
            if apiset[key].get("donation_required") and not self.donation_made:
                raise DonationRequired(f"key {key} requires an account which has donated")

            # check max/min value constraints
            # Special case: When c1 flag is set, v3 represents cumulative lifetime energy values
            # which can exceed the normal maximum validation limit of 200000 Wh
            should_skip_maxval_check = key == "v3" and data.get("c1") is True

            if not should_skip_maxval_check and apiset[key].get("maxval") is not None and data.get(key) > apiset[key].get("maxval"):
                raise ValueError(f"{key} cannot be higher than {apiset[key]['maxval']}, is {value}")

            if apiset[key].get("minval") is not None and data.get(key) < apiset[key].get("minval"):
                raise ValueError(f"{key} cannot be lower than {apiset[key]['minval']}, is {value}")

        return True
