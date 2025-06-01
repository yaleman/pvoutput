"""Interface to the PVOutput API"""

import datetime
from typing import Any, Dict, Optional

import requests

from pvoutput.exceptions import UnknownMethodError

from pvoutput.base import PVOutputBase
from pvoutput.parameters import (
    ADDBATCHSTATUS_PARAMETERS,
    ADDSTATUS_PARAMETERS,
    CALL_PARAMETERS,
    DEFAULT_REQUEST_TIMEOUT,
    ADDOUTPUT_PARAMETERS,
    DELETE_NOTIFICATION_PARAMETERS,
    DELETESTATUS_PARAMETERS,
    REGISTER_NOTIFICATION_PARAMETERS,
)

from . import utils

__version__ = "0.0.8"


class PVOutput(PVOutputBase):
    """This class provides an interface to the pvoutput.org API"""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        apikey: str,
        systemid: int,
        donation_made: bool = False,
        stats_period: int = 5,
        session: Optional[requests.Session] = None,
    ):
        """Setup code
        :param apikey: API key (read or write)
        :type apikey: str
        :param systemid: system ID
        :type systemid: int
        :param donation_made: Whether to use the donation-required fields
        :type donation_made: bool
        """
        super().__init__(
            apikey=apikey,
            systemid=systemid,
            donation_made=donation_made,
            stats_period=stats_period,
        )
        self.session = session
        if session is None:
            self.session = requests.Session()

    def _call(
        self,
        endpoint: str,
        method: str = "POST",
        **kwargs: Dict[str, Any],
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

        self.validate_data(kwargs, CALL_PARAMETERS)

        if method == "GET":
            response = requests.get(
                endpoint,
                data=kwargs.get("data"),
                headers=kwargs.get("headers", self._headers()),
                params=kwargs.get("params"),
                timeout=DEFAULT_REQUEST_TIMEOUT,
            )
        elif method == "POST":
            response = requests.post(
                endpoint,
                data=kwargs.get("data"),
                headers=kwargs.get("headers", self._headers()),
                timeout=DEFAULT_REQUEST_TIMEOUT,
            )
        else:
            raise UnknownMethodError(f"unknown method {kwargs['method']}")

        if response.status_code == 400:
            # TODO: work out how to get the specific response and provide useful answers
            raise ValueError(f"HTTP400: {response.text.strip()}")
        # likely errors - https://pvoutput.org/help/api_specification.html#error-messages
        response.raise_for_status()
        return response

    def check_rate_limit(self) -> Dict[str, str]:
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

    def addbatchstatus(self, data: str, c1: bool = False, n: bool = False) -> requests.Response:
        """
        # Add Batch Status Service

        The Add Batch Status service adds up to 30 statuses in a single request.
        See the documentation on the page for what it means, and what it responds with.
        This hasn't been tested.
        <https://pvoutput.org/help/api_specification.html#add-batch-status-service>

        ## Data Structure

        The data parameter consists of up to 30 statuses, each status contains multiple fields.

        Field Delimiter - ,
        Output Delimiter - ;

        ## Example data

        Send three statuses from 10:00AM to 10:10AM in a single batch request

        `data="20110112,10:00,705,1029;20110112,10:05,775,1320;20110112,10:10,800,800"`

        ## Donation features

        * The d date parameter must be not be older than 90 days from the current date.
        * Extended parameters v7, v8, v9, v10, v11 and v12
        * Maximum energy consumption v3 value increased to 9,999,999Wh
        * Maximum power consumption v4 value increased to 2,000,000W
        * Increased batch status size to 100 from 30
        """
        payload = {
            "data": data,
        }
        if c1:
            payload["c1"] = "1"
        if n:
            payload["n"] = "1"

        url, method = utils.URLS["addbatchstatus"]
        self.validate_data(payload, ADDBATCHSTATUS_PARAMETERS)
        url, method = utils.URLS["addstatus"]
        return self._call(endpoint=url, data=payload, method=method)

    def addstatus(
        self,
        data: Dict[str, Any],
    ) -> requests.Response:
        """The Add Status service accepts live output data
        at the Status Interval (5 to 15 minutes) configured for the system.

        API Spec: https://pvoutput.org/help/api_specification.html#add-status-service

        :param data: The status data
        :type data: dict

        :returns: The response object
        :rtype: requests.Response
        """
        # if you don't set a time, set it to now
        # can't push this through the validator as it relies on the class config
        if "t" not in data:
            data["t"] = self.get_time_by_base()
        self.validate_data(data, ADDSTATUS_PARAMETERS)

        url, method = utils.URLS["addstatus"]

        return self._call(endpoint=url, data=data, method=method)

    def addoutput(
        self,
        data: Dict[str, Any],
    ) -> requests.Response:
        """The Add Output service uploads end of day output information.
        It allows all of the information provided on the Add Output page to be uploaded.

        API Spec: https://pvoutput.org/help/api_specification.html#add-output-service

        :param data: The output data to upload
        :type data: dict

        :returns: The response object
        :rtype: requests.Response
        """
        self.validate_data(data, ADDOUTPUT_PARAMETERS)
        url, method = utils.URLS["addoutput"]
        return self._call(endpoint=url, data=data, method=method)

    def delete_status(self, date_val: datetime.date, time_val: Optional[datetime.time] = None) -> requests.Response:
        """
        Deletes a given status, based on the provided parameters
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
        self.validate_data(
            {
                "date_val": date_val,
                "time_val": time_val,
            },
            DELETESTATUS_PARAMETERS,
        )

        data = {"d": date_val.strftime("%Y%m%d")}
        if time_val is not None:
            data["t"] = time_val.strftime("%H:%M")

        url, method = utils.URLS["deletestatus"]

        return self._call(endpoint=url, data=data, method=method)

    def getstatus(self) -> Dict[str, Any]:
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
        response = self._call(endpoint=url, params=params, method=method)
        response.raise_for_status()
        # grab all the things
        responsedata, extras = utils.responsedata_to_response(response.text.split(","))

        # if we're fancy, we get more data
        if extras:
            for i in range(1, 7):
                responsedata[f"v{i + 6}"] = None if extras[i - 1] == "NaN" else float(extras[i - 1])
        return responsedata

    def register_notification(self, appid: str, url: str, alerttype: int) -> requests.Response:
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

        self.validate_data(
            {
                "appid": appid,
                "url": url,
                "alerttype": alerttype,
            },
            REGISTER_NOTIFICATION_PARAMETERS,
        )

        call_url, method = utils.URLS["registernotification"]
        params = {"appid": appid, "type": alerttype, "url": url}
        return self._call(endpoint=call_url, params=params, method=method)

    def deregister_notification(self, appid: str, alerttype: int) -> requests.Response:
        """The Deregister Notification Service removes registered notifications under an application id for a system.

        API spec: https://pvoutput.org/help/api_specification.html#deregister-notification-service

        All parameters are mandatory

        :param appid: Application ID (eg: example.app.id)
        :type appid: str (maxlen: 100)

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

        self.validate_data(
            {
                "appid": appid,
                "alerttype": alerttype,
            },
            DELETE_NOTIFICATION_PARAMETERS,
        )

        url, method = utils.URLS["deregisternotification"]
        params = {"appid": appid, "type": alerttype}
        return self._call(endpoint=url, params=params, method=method)
