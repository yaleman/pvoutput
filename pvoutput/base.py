""" base class for pvoutput """

from datetime import datetime, time
from math import floor
import re
from typing import Any, AnyStr, Dict, Union

from .exceptions import InvalidRegexpError, DonationRequired


def round_to_base(number: Union[int, float], base: Union[int, float]) -> float:
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

    def _headers(self) -> Dict[str, str]:
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
        format_string: AnyStr,
        key: str,
        value: Any,
    ) -> None:
        """handles the regular expression format checks"""
        try:
            compiled = re.compile(format_string)
            match = compiled.match(value)
            if match is None:
                raise ValueError(
                    f"key '{key}', with value '{value}' does not match '{format_string!r}'"
                )
        except re.error as error:
            raise InvalidRegexpError(
                "Error for key '{key}' with format '{format_string!r}': {error}"
            ) from error

    # pylint: disable=too-many-branches
    def validate_data(self, data: Dict[str, Any], apiset: Dict[str, Any]) -> bool:
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
        if "required_oneof" in apiset.keys() and (
            len([key for key in data.keys() if key in apiset["required_oneof"]["keys"]])
            == 0
        ):
            raise ValueError(
                f"one of {','.join(apiset['required_oneof']['keys'])} MUST be set"
            )
        for key in apiset.keys():
            # check that that required values are set
            if apiset[key].get("required", False) and key not in data.keys():
                if "default" in apiset[key]:
                    # set a default value
                    data[key] = apiset[key]["default"]
                else:
                    raise ValueError(f"key {key} required in data")

            # check maxlen
            if "maxlen" in apiset[key] and key in data:
                if len(data[key]) > apiset[key]["maxlen"]:
                    raise ValueError(
                        f"Value too long for key {key} {len(data[key])}>{apiset[key]['maxlen']}"
                    )

            # check the value is in the set of valid choices
            if "choices" in apiset[key] and key in data:
                if data[key] not in apiset[key]["choices"]:
                    raise ValueError(
                        f"Invalid value for key {key}: '{data[key]}', should be in {apiset[key]['choices']} "
                    )

        # check there's no extra fields in the data
        for key in data:
            if key not in apiset.keys():
                raise ValueError(f"key {key} isn't valid in the API spec")

            if apiset[key].get("type") and not isinstance(
                data[key], apiset[key]["type"]
            ):
                if data[key] is not None:
                    raise TypeError(
                        f"data[{key}] type ({type(data[key])} is invalid - should be {str(apiset[key]['type'])})"
                    )

        for key in data:
            if "format" in apiset[key]:
                self._validate_format(apiset[key]["format"], key, data[key])
            # can run additional functions over the data
            if "additional_validators" in apiset[key]:
                for validator in apiset[key]["additional_validators"]:
                    validator(data[key])

            # TODO: 'd' can't be more than 14 days ago, if a donator, goes out to 90
            # check if donation_made == True and age of thing
            # if self.donation_made:
            #     # check if more than 90 days ago
            # else:
            #     # check if more than 14 days ago

            # check for donation-only keys
            if apiset[key].get("donation_required") and not self.donation_made:
                raise DonationRequired(
                    f"key {key} requires an account which has donated"
                )
            # check if you're outside max/min values
            if apiset[key].get("maxval") and data.get(key) > apiset[key].get("maxval"):
                raise ValueError(
                    f"{key} cannot be higher than {apiset[key]['maxval']}, is {data[key]}"
                )
            if apiset[key].get("minval") and data.get(key) < apiset[key].get("minval"):
                raise ValueError(
                    f"{key} cannot be lower than {apiset[key]['minval']}, is {data[key]}"
                )

        return True
