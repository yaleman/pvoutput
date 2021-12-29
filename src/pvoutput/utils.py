""" Utilities """
import json
import os
from datetime import datetime
from math import floor

from .exceptions import DonationRequiredError, ConfigurationNotFoundError

BASE_URL = "https://pvoutput.org/service/r2/"

URLS = {
    "addstatus": (
        BASE_URL + "addstatus.jsp",
        "POST",
    ),
    "getsystem": (
        BASE_URL + "getsystem.jsp",
        "GET",
    ),
    "getstatus": (
        BASE_URL + "getstatus.jsp",
        "GET",
    ),
    "deletestatus": (
        BASE_URL + "deletestatus.jsp",
        "POST",
    ),
    "registernotification": (
        BASE_URL + "registernotification.jsp",
        "GET",
    ),
    "deregisternotification": (
        BASE_URL + "deregisternotification.jsp",
        "GET",
    ),
}


def round_to_base(number, base):
    """rounds down to a specific base number
    based on answer in https://stackoverflow.com/a/2272174/188774
    """
    return base * round(floor(number / base))


def responsedata_to_response(input_data: list):
    """ Turns the status output into a dict """
    # pylint: disable=invalid-name
    d, t, v1, v2, v3, v4, v5, v6, normalised_output, *extras = input_data

    # if there's no data, you get "NaN". Here we change that to NoneType
    responsedata = {
        "d": d,
        "t": t,
        "timestamp": datetime.strptime(f"{d} {t}", "%Y%m%d %H:%M"),
        "v1": None if v1 == "NaN" else float(v1),
        "v2": None if v2 == "NaN" else float(v2),
        "v3": None if v3 == "NaN" else float(v3),
        "v4": None if v4 == "NaN" else float(v4),
        "v5": None if v5 == "NaN" else float(v5),
        "v6": None if v6 == "NaN" else float(v6),
        "normalised_output": float(normalised_output),
    }
    return responsedata, extras


def get_rate_limit_header(response_object) -> dict:
    """ gets the rate limit header from the returned headers """
    retval = {}
    for key in response_object.headers.keys():
        if key.startswith("X-Rate-Limit"):
            retval[key] = response_object.headers[key]
    return retval


def validate_data(data: dict, apiset: dict, donation_made: bool = False) -> bool:
    """Does a super-simple validation based on the api def raises errors if it's wrong, returns True if it's OK

    This will only raise an error on the first error it finds

    :param data: the data to validate.
    :type data: dict

    :param apiset: A set of validation rules, eg: pvoutput.ADDSTATUS_PARAMETERS
    :type apiset: dict

    :param donation_made: has a pvoutput donation been made
    :type donation_made: bool

    :raises TypeError: if the type testing fails.
    :raises ValueError: if you're trying to pass an invalid value.
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
            raise ValueError(f"key {key} required in data")
    # check there's no extras
    for key in data.keys():
        if key not in apiset.keys():
            raise ValueError(f"key {key} isn't valid in the API spec")
        if apiset[key].get("type", False) and not isinstance(
            data[key], apiset[key]["type"]
        ):
            raise TypeError(
                f"data[{key}] type ({type(data[key])} is invalid - should be {str(type(apiset[key]['type']))})"
            )
    # TODO: check format, 'format' should be a regex
    # for format_string in [apiset[key].get("format") for key in apiset.keys()]:
    #     print(format_string)

    # TODO: 'd' can't be more than 14 days ago, if a donator, goes out to 90
    # check if donation_made == True and age of thing
    # if self.donation_made:
    #     # check if more than 90 days ago
    # else:
    #     # check if more than 14 days ago

    # check for donation-only keys
    if not donation_made:
        donation_required_keys = [
            key for key in data.keys() if apiset[key].get("donation_required", False)
        ]
        for key in data.keys():
            if key in donation_required_keys:
                raise DonationRequiredError(
                    f"key {key} requires an account which has donated"
                )
    if int(data.get("v3", 0)) > 200000:
        raise ValueError(f"v3 cannot be higher than 200000, is {data['v3']}")
    if int(data.get("v4", 0)) > 100000:
        raise ValueError(f"v4 cannot be higher than 100000, is {data['v4']}")

    return True


def get_apikey_systemid_from_config(config_file_name: str = None) -> tuple[str, int]:
    """read a pvoutput.json files with apikey and systemid values
    ```
    {
        "apikey": "aaaaaabbbbbbccccccddddddeeeeeeffffffgggg",
        "systemid": 12345
    }
    ```
    If parameter config_file_name is provided, that is first tried
    if not found then the user home dir ~/.config/pvoutput.json is tried,
    if not found then config/pvoutput.json is tried from the current dir

    :param config_file_name: the filename to read the configuration from
    :type config_file_name: str

    :return: a tuple with apikey, systemid
    :rtype: tuple[str, int]
    """
    if config_file_name is None or not os.path.exists(config_file_name):
        config_file_name = os.path.expanduser("~/.config/pvoutput.json")
        if not os.path.exists(config_file_name):
            config_file_name = "config/pvoutput.json"
            if not os.path.exists(config_file_name):
                raise ConfigurationNotFoundError()

    with open(config_file_name, 'r') as config_file:
        config = json.load(config_file)

    return config.get("apikey"), int(config.get("systemid"))
