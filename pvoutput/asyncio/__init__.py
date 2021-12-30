""" AsyncIO interface to the PVOutput API """

import datetime
import re

import asyncio
import aiohttp

from ..parameters import *
from .. import utils


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
        session=None,
    ):
        """Startup phase
        ```
        :param apikey: API key (read or write)
        :type apikey: str
        :param systemid: system ID
        :type systemid: int
        :param donation_made: Whether to use the donation-required fields
        :type donation_made: bool
        ```
        """
        self.session = session
        if not session:
            self.session = aiohttp.ClientSession()

        if not isinstance(systemid, int):
            raise TypeError("systemid should be int")
        if not isinstance(apikey, str):
            raise TypeError("apikey should be str")
        self.apikey = apikey
        self.systemid = systemid
        self.donation_made = donation_made
        self.stats_period = stats_period

    def _headers(self) -> dict:
        """
        Relevant documentation: https://pvoutput.org/help.html#api-spec

        :return: headers for calls to the API
        :rtype: dict
        """
        headers = {
            "X-Pvoutput-Apikey": self.apikey,
            "X-Pvoutput-SystemId": str(self.systemid),
        }
        return headers

    async def _call(
        self, endpoint, data=None, params=None, headers=False, method: str = "POST"
    ):
        """Makes a call to a URL endpoint with the data/headers/method you require.

        :param endpoint: The URL to call
        :type endpoint: str

        :param data: Data to send
        :type data: dict

        :param headers: Additional headers, if unset it'll use self._headers() which is the standard API key / systemid set (eg, self.check_rate_limit)
        :type headers: dict

        :param method: specify a method if you want to use something other than requests.post
        :type method: requests.request

        :returns: The method.response object
        :rtype: method.response

        :raises TypeError: if the data you pass is of the wrong format.
        :raises ValueError: if the call throws a HTTP 400 error.
        :raises requests.exception: if method throws an exception.
        """
        if not method:
            method = self.session.post

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
            response = await self.session.get(
                endpoint, data=data, headers=headers, params=params
            )
        else:
            response = await self.session.post(endpoint, data=data, headers=headers)

        if response.status == 400:
            # TODO: work out how to get the specific response and provide useful answers
            raise ValueError(f"HTTP400: {response.text.strip()}")
        # likely errors - https://pvoutput.org/help/api_specification.html#error-messages
        response.raise_for_status()
        return response

    async def check_rate_limit(self) -> dict:
        """
        Makes a call to the site, checking if you have hit the rate limit.
        Check the [documentation](https://pvoutput.org/help/api_specification.html#rate-limits)

        :returns: the headers relating to the rate limit.
        :rtype: dict

        """
        headers = self._headers()
        headers["X-Rate-Limit"] = "1"

        url, method = utils.URLS["getsystem"]

        response = await self._call(url, {}, headers=headers, method=method)
        retval = utils.get_rate_limit_header(response)

        return retval

    async def addstatus(self, data: dict):
        """
        The Add Status service accepts live output data at the status interval (5 to 15 minutes) configured for the system.

        API Spec: https://pvoutput.org/help.html#api-addstatus

        :param data: The status data
        :type data: dict

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

        return await self._call(endpoint=url, data=data, method=method)

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

    async def delete_status(self, date_val: datetime.datetime.date, time_val=None):
        """deletes a given status, based on the provided parameters
        needs a datetime() object
        set the hours/minutes to non-zero to delete a specific time

        :param date_val: The date to delete.
        :type date_val: datetime.datetime.date

        :param time_val: The time entry to delete.
        :type time_val: datetime.datetime.time

        :returns: the response object
        :rtype: requests.post
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
        response = self._call(
            endpoint="https://pvoutput.org/service/r2/deletestatus.jsp", data=data
        )
        return response

    async def getstatus(self) -> dict:
        """
        Makes a call to the API and gets the last update.


        :returns: the last updated data
        :rtype: dict
        """
        # TODO: extend this, you can do history searches and all sorts with this endpoint
        url = "https://pvoutput.org/service/r2/getstatus.jsp"
        data = {}
        if self.donation_made:
            url = f"{url}?ext=1&sid={self.systemid}"
        response = await self._call(endpoint=url, data=data, method="GET")

        # grab all the things
        text = await response.text()

        responsedata, extras = utils.responsedata_to_response(text.split(","))

        # if we're fancy, we get more data
        if extras:
            for i in range(1, 7):
                responsedata[f"v{i+6}"] = (
                    None if extras[i - 1] == "NaN" else float(extras[i - 1])
                )
        return responsedata

    async def register_notification(self, appid: str, url: str, alerttype: int) -> str:
        """
        The Register Notification Service allows a third party application
        to receive PVOutput alert callbacks via a HTTP end point.

        [API Documentation](https://pvoutput.org/help/api_specification.html#register-notification-service)

        All parameters are mandatory:

        ```
        :param appid: Application ID (eg: example.app.id)
        :type appid: str (maxlen: 100)

        :param url: Callback URL (eg: http://example.com/api/)
        :type url: str (maxlen: 150)

        :param alerttype: Alert Type (See list below)
        :type alerttype: int

        :return: The response text
        :rtype: str

        ```
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
        ```
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
        return await (
            await self._call(endpoint=call_url, params=params, method=method)
        ).text()
