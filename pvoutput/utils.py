""" Utilities """

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Tuple

__all__ = [
    "URLS",
    "validate_delete_status_date",
    "ALERT_TYPES",
]

BASE_URL = "https://pvoutput.org/service/r2/"

URLS = {
    "addstatus": (
        BASE_URL + "addstatus.jsp",
        "POST",
    ),
    "addoutput": (
        BASE_URL + "addoutput.jsp",
        "POST",
    ),
    "deletestatus": (
        BASE_URL + "deletestatus.jsp",
        "POST",
    ),
    "getstatus": (
        BASE_URL + "getstatus.jsp",
        "GET",
    ),
    "getsystem": (
        BASE_URL + "getsystem.jsp",
        "GET",
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

ALERT_TYPES = {
    0: "All Notifications",
    1: "Private Message",
    3: "Joined Team",
    4: "Added Favourite",
    5: "High Consumption Alert",
    6: "System Idle Alert",
    8: "Low Generation Alert",
    11: "Performance Alert",
    14: "Standby Cost Alert",
    15: "Extended Data V7 Alert",
    16: "Extended Data V8 Alert",
    17: "Extended Data V9 Alert",
    18: "Extended Data V10 Alert",
    19: "Extended Data V11 Alert",
    20: "Extended Data V12 Alert",
    23: "High Net Power Alert",
    24: "Low Net Power Alert",
}


def responsedata_to_response(input_data: List[str]) -> Tuple[Dict[str, Any], List[str]]:
    """Turns the status output into a dict"""
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


def get_rate_limit_header(response_object: Any) -> Dict[str, str]:
    """gets the rate limit header from the returned headers"""
    retval = {}
    for key in response_object.headers.keys():
        if key.startswith("X-Rate-Limit"):
            retval[key] = str(response_object.headers[key])
    return retval


def validate_delete_status_date(date_val: date) -> None:
    """runs the validation for the date_val option of delete_status"""
    yesterday = date.today() - timedelta(days=1)
    tomorrow = date.today() + timedelta(days=1)
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
