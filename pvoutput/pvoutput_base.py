import datetime
import functools
import re

from . import utils
from .exceptions import *


class PVOutputBase:
    def __init__(
        self,
        apikey: str,
        systemid: int,
        donation_made: bool = False,
        stats_period: int = 5,
    ):
        if not isinstance(systemid, int):
            raise TypeError("systemid should be int")
        if not isinstance(apikey, str):
            raise TypeError("apikey should be str")
        self.apikey = apikey
        self.systemid = systemid
        self.donation_made = donation_made
        self.stats_period = stats_period

    def _headers(self) -> dict:
        """Relevant documentation: https://pvoutput.org/help/api_specification.html#http-headers

        :return: headers for calls to the API
        :rtype: dict
        """
        headers = {
            "X-Pvoutput-Apikey": self.apikey,
            "X-Pvoutput-SystemId": str(self.systemid),
        }
        return headers

    # pylint: disable=too-many-branches
    def validate_data(self, data, apiset):
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
        for key in apiset:
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
                    f"data[{key}] type ({type(data[key])} is invalid - should be {str(apiset[key]['type'])})"
                )

        for key in data:
            format_string = apiset[key].get("format", False)
            if format_string:
                try:
                    compiled = re.compile(format_string)
                    match = compiled.match(data[key])
                    if match is None:
                        raise ValueError(
                            f"key '{key}', with value '{data[key]}' does not match '{format_string}'"
                        )
                except re.error as error:
                    raise InvalidRegexpError(
                        f"Error for key '{key}' with format '{format_string}': {error}"
                    ) from error

        # TODO: 'd' can't be more than 14 days ago, if a donator, goes out to 90
        # check if donation_made == True and age of thing
        # if self.donation_made:
        #     # check if more than 90 days ago
        # else:
        #     # check if more than 14 days ago

        # check for donation-only keys
        if not self.donation_made:
            donation_required_keys = [
                key
                for key in data.keys()
                if apiset[key].get("donation_required", False)
            ]
            for key in data.keys():
                if key in donation_required_keys:
                    raise DonationRequired(
                        f"key {key} requires an account which has donated"
                    )
        if int(data.get("v3", 0)) > 200000:
            raise ValueError(f"v3 cannot be higher than 200000, is {data['v3']}")
        if int(data.get("v4", 0)) > 100000:
            raise ValueError(f"v4 cannot be higher than 100000, is {data['v4']}")

        return True

    @staticmethod
    def _call_validator():
        """_call arguments validator"""

        def decorator_validator(func):
            @functools.wraps(func)
            def wrapper_validator(self, *args, **kwargs):

                # always need the base headers
                if "headers" not in kwargs:
                    kwargs["headers"] = self._headers()
                # TODO: type checking on call
                if (
                    kwargs["method"] == "POST"
                    and kwargs["data"]
                    and isinstance(kwargs["data"], dict) is False
                ):
                    raise TypeError(
                        f"data should be a dict, got {str(type(kwargs['data']))}"
                    )
                if (
                    kwargs["method"] == "GET"
                    and kwargs["params"]
                    and isinstance(kwargs["params"], dict) is False
                ):
                    raise TypeError(
                        f"params should be a dict, got {str(type(kwargs['params']))}"
                    )
                if kwargs["headers"] and not isinstance(kwargs["headers"], dict):
                    raise TypeError(
                        f"headers should be a dict, got {str(type(kwargs['headers']))}"
                    )

                return func(self, *args, **kwargs)

            return wrapper_validator

        return decorator_validator

    @staticmethod
    def _data_validator(apiset):
        """data argument validator with apiset"""

        def decorator_validator(func):
            @functools.wraps(func)
            def wrapper_validator(self, *args, **kwargs):

                data = None
                if "data" in kwargs:
                    data = kwargs["data"]
                elif len(args):
                    data = args[0]

                self.validate_data(data, apiset)

                return func(self, *args, **kwargs)

            return wrapper_validator

        return decorator_validator

    @staticmethod
    def _addstatus_validator():
        """addstatus arguments validator"""

        def decorator_validator(func):
            @functools.wraps(func)
            def wrapper_decorator(self, *args, **kwargs):

                data = None
                if "data" in kwargs:
                    data = kwargs["data"]
                elif len(args):
                    data = args[0]

                if not data.get("d", False):
                    # if you don't set a date, make it now
                    data["d"] = datetime.date.today().strftime("%Y%m%d")
                if not data.get("t", False):
                    # if you don't set a time, set it to now

                    hour = int(datetime.datetime.now().strftime("%H"))
                    # round the minute to the current stats period
                    minute = utils.round_to_base(
                        datetime.datetime.now().minute, self.stats_period
                    )
                    data["t"] = datetime.time(hour=hour, minute=minute).strftime(
                        "%H:%M"
                    )

                return func(self, *args, **kwargs)

            return wrapper_decorator

        return decorator_validator

    @staticmethod
    def _addoutput_validator():
        """addoutput arguments validator"""

        def decorator_validator(func):
            @functools.wraps(func)
            def wrapper_decorator(self, *args, **kwargs):

                data = None
                if "data" in kwargs:
                    data = kwargs["data"]
                elif len(args):
                    data = args[0]

                if not data.get("d", False):
                    # if you don't set a date, make it now
                    data["d"] = datetime.date.today().strftime("%Y%m%d")

                return func(self, *args, **kwargs)

            return wrapper_decorator

        return decorator_validator

    @staticmethod
    def _delete_status_validator():
        """deletestatus arguments validator"""

        def decorator_validator(func):
            @functools.wraps(func)
            def wrapper_decorator(self, *args, **kwargs):

                date_val = None
                if "date_val" in kwargs:
                    date_val = kwargs["date_val"]
                elif len(args) > 0:
                    date_val = args[0]

                time_val = None
                if "time_val" in kwargs:
                    time_val = kwargs["time_val"]
                elif len(args) > 1:
                    time_val = args[1]

                if not isinstance(date_val, datetime.date):
                    raise ValueError(
                        f"date_val should be of type datetime.date, not {type(date_val)}"
                    )
                if time_val and not isinstance(time_val, datetime.time):
                    raise ValueError(
                        f"time_val should be of time datetime.time, not {type(time_val)}"
                    )
                yesterday = datetime.date.today() - datetime.timedelta(1)
                tomorrow = datetime.date.today() + datetime.timedelta(1)
                # you can't delete back past yesterday
                if date_val < yesterday:
                    raise ValueError(
                        f"date_val can only be yesterday or today, you provided {date_val}"
                    )
                # you can't delete forward of today
                if date_val >= tomorrow:
                    raise ValueError(
                        f"date_val can only be yesterday or today, you provided {date_val}"
                    )

                return func(self, *args, **kwargs)

            return wrapper_decorator

        return decorator_validator

    @staticmethod
    def _register_notification_validator():
        def decorator_validator(func):
            @functools.wraps(func)
            def wrapper_decorator(self, *args, **kwargs):

                if "appid" in kwargs:
                    appid = kwargs["appid"]
                else:
                    appid = args[0]
                if "url" in kwargs:
                    url = kwargs["url"]
                else:
                    url = args[1]
                if "alerttype" in kwargs:
                    alerttype = kwargs["alerttype"]
                else:
                    alerttype = args[2]

                if not isinstance(appid, str):
                    raise TypeError(
                        f"appid needs to be a string, got: {str(type(appid))}"
                    )
                if not isinstance(url, str):
                    raise TypeError(f"url needs to be a string, got: {str(type(url))}")
                if len(url) > 150:
                    raise ValueError(
                        f"Length of url can't be longer than 150 chars - was {len(url)}"
                    )
                if len(appid) > 100:
                    raise ValueError(
                        f"Length of appid can't be longer than 100 chars - was {len(appid)}"
                    )

                if not isinstance(alerttype, int) or alerttype not in utils.ALERT_TYPES:
                    raise UnknownAlertTypeError(
                        f"alerttype is unknown, got: {type(alerttype)} - {alerttype}"
                    )
                return func(self, *args, **kwargs)

            return wrapper_decorator

        return decorator_validator

    @staticmethod
    def _deregister_notification_validator():
        def decorator_validator(func):
            @functools.wraps(func)
            def wrapper_decorator(self, *args, **kwargs):

                if "appid" in kwargs:
                    appid = kwargs["appid"]
                else:
                    appid = args[0]
                if "alerttype" in kwargs:
                    alerttype = kwargs["alerttype"]
                else:
                    alerttype = args[1]

                if not isinstance(appid, str):
                    raise TypeError(
                        f"appid needs to be a string, got: {str(type(appid))}"
                    )
                if len(appid) > 100:
                    raise ValueError(
                        f"Length of appid can't be longer than 100 chars - was {len(appid)}"
                    )

                if not isinstance(alerttype, int) or alerttype not in utils.ALERT_TYPES:
                    raise UnknownAlertTypeError(
                        f"alerttype is unknown, got: {type(alerttype)} - {alerttype}"
                    )
                return func(self, *args, **kwargs)

            return wrapper_decorator

        return decorator_validator
