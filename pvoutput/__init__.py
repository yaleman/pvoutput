""" provides an class for uploading to the PVOutput API """

name = "pvoutput"

import requests
from datetime import datetime, date, timedelta, time

from .parameters import *

class PVOutput(object):
    def __init__(self, apikey: str, systemid: int, donation_made: bool = False):
        if not isinstance(systemid, int):
            raise TypeError("systemid should be int")
        if not isinstance(apikey, str):
            raise TypeError("apikey should be str")
        self.apikey = apikey
        self.systemid = systemid
        self.donation_made = donation_made

    def _headers(self):
        """ returns a base dict of headers for calls to the API 
        Documentation: https://pvoutput.org/help.html#api-spec
        """
        headers = {
            "X-Pvoutput-Apikey": self.apikey,
            "X-Pvoutput-SystemId": str(self.systemid),
        }
        return headers

    def _call(self, endpoint, data, headers=False, method=requests.post):
        """ makes a call to a URL endpoint with the data/headers/method you require
        specify headers if you need to set additional ones, otherwise it'll use self._headers() which is the standard API key / systemid set (eg, self.check_rate_limit)
        specify a method if you want to use something other than requests.post
        """
        if not headers:
            headers = self._headers()
        retval = method(endpoint, data=data, headers=headers)

        if retval.status_code == 200:
            return retval
        elif retval.status_code == 400:
            # TODO: work out how to get the specific response and provide useful answers
            raise ValueError(f"HTTP400: {retval.text.strip()}")
            # return False
        else:
            raise ValueError(f"HTTP{retval.status_code}: {retval.text.strip()}")
        # other possible errors
        # Method Not Allowed 405: POST or GET only 	 - if we get that, wtf?
        # Data must be sent via the HTTP POST or GET method

        # Unauthorized 401: Invalid System ID
        # # The required parameter X-Pvoutput-SystemId or sid is missing from the request. The sid is a number which identifies a system. The sid can be obtained from the Settings page under Registered Systems.

        # Unauthorized 401: Invalid API Key
        # The API key is missing in the header request or the API key is invalid.

        # Unauthorized 401: Disabled API Key
        # The API key has not been enabled in the Settings.

        # Forbidden 403: Read only key
        # The API key provided is a read only key and cannot access the requested service which updates system data, use the standard key to update system data.

        # Unauthorized 401: Missing, invalid or inactive api key information (X-Pvoutput-Apikey)
        # The sid and key combination is invalid

        # Forbidden 403: Exceeded number requests per hour
        # The maximum number of requests per hour has been reached for the API key. Wait till the next hour before making further requests.

        # Forbidden 403: Donation Mode
        # Request is only available in donation mode.

    def check_rate_limit(self):
        headers = self._headers()
        headers["X-Rate-Limit"] = "1"
        url = "https://pvoutput.org/service/r2/getstatus.jsp"
        response = self._call(url, {}, headers=headers)
        retval = {}
        for key in response.headers.keys():
            if key.startswith("X-Rate-Limit"):
                retval[key] = response.headers[key]
        return retval

    def addstatus(self, data: dict):
        """ The Add Status service accepts live output data at the status interval (5 to 15 minutes) configured for the system.
        API Spec: https://pvoutput.org/help.html#api-addstatus
        """
        self.validate_data(data, ADDSTATUS_PARAMETERS)

        return NotImplementedError("haven't got addstatus() working yet")
        self._call(endpoint="https://pvoutput.org/service/r2/addstatus.jsp", data)

    def addoutput(self, data):
        """ The Add Output service uploads end of day output information. It allows all of the information provided on the Add Output page to be uploaded. 
        API Spec: https://pvoutput.org/help.html#api-addoutput """
        self.validate_data(data, ADDOUTPUT_PARAMETERS)
        return NotImplementedError("haven't got this addoutput() yet")
        self._call(endpoint="https://pvoutput.org/service/r2/addoutput.jsp", data=data)

    def delete_status(self, date_val: datetime.date, time_val=None):
        """ deletes a given status, based on the provided parameters 
            needs a datetime() object
            set the hours/minutes to non-zero to delete a specific time

            returns a requests.post response object
        """
        if not isinstance(date_val, date):
            raise ValueError(
                f"date_val should be of type datetime.datetime, not {type(date_val)}"
            )
        if time_val and not isinstance(time_val, time):
            raise ValueError(
                f"time_val should be of time datetime.time, not {type(time_val)}"
            )
        yesterday = date.today() - timedelta(1)
        tomorrow = date.today() + timedelta(1)
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

    def validate_data(self, data, apiset):
        """ does a super-simple validation based on the api def raises errors if it's wrong, returns True if it's OK
            WARNING: will only raise an error on the first error it finds
            eg: pvoutput.PVOutput.validate_data(data, pvoutput.ADDSTATUS_PARAMETERS)
        """
        # if you set a 'required_oneof' key in apiset, validation will require at least one of those keys to be set
        if "required_oneof" in apiset.keys():
            if (
                len(
                    [
                        key
                        for key in data.keys()
                        if key in apiset["required_oneof"]["keys"]
                    ]
                )
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
            if apiset[key].get("type", False):
                if not isinstance(data[key], apiset[key]["type"]):
                    raise TypeError(
                        f"data[{key}] type ({type(data[key])} is invalid - should be {type(apiset[key]['type'])})"
                    )
        # TODO: check format, 'format' should be a regex

        # TODO: 'd' can't be more than 14 days ago, if a donator, goes out to 90
        # check if donation_mode == True and age of thing

        # TODO: check for donation-only keys
        if not self.donation_made:
            donation_required_keys = [
                key
                for key in data.keys()
                if apiset[key].get("donation_required", False)
            ]
            for key in data.keys():
                if key in donation_required_keys:
                    raise ValueError(f"key {key} requires an account which has donated")

        # TODO: 'v3' can't be higher than 200000
        # TODO: 'v4' can't be higher than 100000
        return True
