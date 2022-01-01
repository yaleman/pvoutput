""" Synchronous interface to the PVOutput API """

import datetime

import requests

from .parameters import *
from .exceptions import *

from . import utils


__version__ = "0.0.8"


class PVOutput:
    """This class provides an interface to the pvoutput.org API"""

    validate_data = utils.validate_data

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        apikey: str,
        systemid: int,
        donation_made: bool = False,
        stats_period: int = 5,
    ):
        """Setup code

        :param apikey: API key (read or write)
        :type apikey: str
        :param systemid: system ID
        :type systemid: int
        :param donation_made: Whether to use the donation-required fields
        :type donation_made: bool
        """
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

    def _call(
        self, endpoint, data=None, params=None, headers=False, method: str = "POST"
    ) -> requests.Response:
        """Makes a call to a URL endpoint with the data/headers/method you require.

        :param endpoint: The URL to call
        :type endpoint: str

        :param data: Data to send
        :type data: dict

        :param headers: Additional headers, if unset it'll use self._headers() which is the standard API key / systemid set (eg, self.check_rate_limit)
        :type headers: dict

        :param method: specify a method if you want to use something other than POST
        :type method: str

        :returns: The response object
        :rtype: requests.Response

        :raises TypeError: if the data you pass is of the wrong format.
        :raises ValueError: if the call throws a HTTP 400 error.
        :raises requests.exception: if method throws an exception.
        """
        # always need the base headers
        if not headers:
            headers = self._headers()
        # TODO: type checking on call
        if method == "POST" and data and isinstance(data, dict) is False:
            raise TypeError(f"data should be a dict, got {str(type(data))}")
        if method == "GET" and params and isinstance(params, dict) is False:
            raise TypeError(f"params should be a dict, got {str(type(params))}")
        if headers and not isinstance(headers, dict):
            raise TypeError(f"headers should be a dict, got {str(type(headers))}")
        # TODO: learn if I can dynamically send thing, is that **args?
        if method == "GET":
            response = requests.get(endpoint, data=data, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(endpoint, data=data, headers=headers)
        else:
            raise UnknownMethodError(f"unknown method {method}")

        if response.status_code == 400:
            # TODO: work out how to get the specific response and provide useful answers
            raise ValueError(f"HTTP400: {response.text.strip()}")
        # likely errors - https://pvoutput.org/help/api_specification.html#error-messages
        response.raise_for_status()
        return response

    def check_rate_limit(self) -> dict:
        """Makes a call to the site, checking if you have hit the rate limit.

        API spec: https://pvoutput.org/help/api_specification.html#rate-limits

        :returns: the headers relating to the rate limit.
        :rtype: dict
        """
        headers = self._headers()
        headers["X-Rate-Limit"] = "1"

        url, method = utils.URLS["getsystem"]

        response = self._call(endpoint=url, params={}, headers=headers, method=method)
        retval = utils.get_rate_limit_header(response)
        return retval

    def addstatus(self, data: dict) -> requests.Response:
        """The Add Status service accepts live output data
        at the Status Interval (5 to 15 minutes) configured for the system.

        API Spec: https://pvoutput.org/help/api_specification.html#add-status-service

        :param data: The status data
        :type data: dict

        :returns: The response object
        :rtype: requests.Response
        """
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
            data["t"] = datetime.time(hour=hour, minute=minute).strftime("%H:%M")
        self.validate_data(data, ADDSTATUS_PARAMETERS)

        url, method = utils.URLS["addstatus"]

        return self._call(endpoint=url, data=data, method=method)

    # def addoutput(self, data: dict):
    #     """ The Add Output service uploads end of day output information. It allows all of the information provided on the Add Output page to be uploaded.

    #     API Spec: https://pvoutput.org/help.html#api-addoutput

    #     :param data: The output data to upload
    #     :type data: dict

    #     :raises NotImplementedError: If you use it, because I haven't got to this yet.
    #     """
    #     return NotImplementedError("Haven't Implemented pvoutput.addoutput() yet.")
    #     # self.validate_data(data, ADDOUTPUT_PARAMETERS)
    #     # self._call(endpoint="https://pvoutput.org/service/r2/addoutput.jsp", data=data)

    def delete_status(
        self, date_val: datetime.datetime, time_val=None
    ) -> requests.Response:
        """Deletes a given status, based on the provided parameters
        needs a datetime() object
        set the hours/minutes to non-zero to delete a specific time

        API spec: https://pvoutput.org/help/api_specification.html#delete-status-service

        :param date_val: The date to delete.
        :type date_val: datetime.datetime.date

        :param time_val: The time entry to delete.
        :type time_val: datetime.datetime.time

        :returns: The response object
        :rtype: requests.Response
        """
        if not isinstance(date_val, datetime.date):
            raise ValueError(
                f"date_val should be of type datetime.datetime.datetime, not {type(date_val)}"
            )
        if time_val and not isinstance(time_val, datetime.time):
            raise ValueError(
                f"time_val should be of time datetime.datetime.time, not {type(time_val)}"
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
        data = {"d": date_val.strftime("%Y%m%d")}
        if time_val:
            data["t"] = time_val.strftime("%H:%M")

        url, method = utils.URLS["deletestatus"]

        return self._call(endpoint=url, data=data, method=method)

    # pylint: disable=too-many-locals
    def getstatus(self) -> dict:
        """The Get Status service retrieves system status information and live output data.

        API spec: https://pvoutput.org/help/api_specification.html#get-status-service

        :returns: the last updated data
        :rtype: dict
        """
        # TODO: extend this, you can do history searches and all sorts with this endpoint

        params = {}
        if self.donation_made:
            params["ext"] = 1
            params["sid"] = self.systemid
        url, method = utils.URLS["getstatus"]
        response = self._call(endpoint=url, params=params, data=None, method=method)
        response.raise_for_status()
        # grab all the things
        # pylint: disable=invalid-name
        responsedata, extras = utils.responsedata_to_response(response.text.split(","))

        # if we're fancy, we get more data
        if extras:
            for i in range(1, 7):
                responsedata[f"v{i+6}"] = (
                    None if extras[i - 1] == "NaN" else float(extras[i - 1])
                )
        return responsedata

    def register_notification(
        self, appid: str, url: str, alerttype: int
    ) -> requests.Response:
        """The Register Notification Service allows a third party application
        to receive PVOutput alert callbacks via a HTTP end point.

        API spec: https://pvoutput.org/help/api_specification.html#register-notification-service

        All parameters are mandatory

        :param appid: Application ID (eg: example.app.id)
        :type appid: str (maxlen: 100)

        :param url: Callback URL (eg: http://example.com/api/)
        :type url: str (maxlen: 150)

        :param alerttype: Alert Type (See list below)
        :type alerttype: int

        :return: The response object
        :rtype: requests.Response

        Alert Type list:

        =====   ====
        Value   Type
        =====   ====
        0       All Notifications
        1       Private Message
        3       Joined Team
        4       Added Favourite
        5       High Consumption Alert
        6       System Idle Alert
        8       Low Generation Alert
        11      Performance Alert
        14      Standby Cost Alert
        15      Extended Data V7 Alert
        16      Extended Data V8 Alert
        17      Extended Data V9 Alert
        18      Extended Data V10 Alert
        19      Extended Data V11 Alert
        20      Extended Data V12 Alert
        23      High Net Power Alert
        24      Low Net Power Alert
        =====   ====
        """
        # TODO: Find out if HTTPS is supported for Callback URLs
        # TODO: validation of types, is this the best way?
        # validation of inputs
        if not isinstance(appid, str):
            raise TypeError(f"appid needs to be a string, got: {str(type(appid))}")
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

        if not isinstance(alerttype, int):
            raise TypeError(
                f"alerttype needs to be an int, got: {str(type(alerttype))}"
            )

        call_url, method = utils.URLS["registernotification"]
        # no need to encode parameters, requests library does this
        params = {"appid": appid, "type": alerttype, "url": url}
        return self._call(endpoint=call_url, params=params, method=method)
