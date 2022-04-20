""" Standard parameter things. """

from copy import copy
from datetime import date, datetime, time


from .utils import ALERT_TYPES, validate_delete_status_date

__all__ = [
    "ADDOUTPUT_PARAMETERS",
    "ADDSTATUS_PARAMETERS",
    "CALL_PARAMETERS",
    "DELETESTATUS_PARAMETERS",
    "DELETE_NOTIFICATION_PARAMETERS",
    "REGISTER_NOTIFICATION_PARAMETERS",
]

standard_parameters = {
    "d": {
        "required": True,
        "description": "Date",
        "format": r"^(20\d{2})(\d{2})(\d{2})$",
        "type": str,
        "donation_required": False,
        "default": datetime.today().strftime("%Y%m%d"),
    },
    "t": {
        "required": True,
        "description": "Time",
        "format": r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$",
        "type": str,
        "donation_required": False,
        "default": datetime.now().strftime("%H:%M"),
    },  # TODO: the validator is terrible
}

CALL_PARAMETERS = {
    "data": {
        "required": False,
        "type": dict,
        "donation_required": False,
        "default": None,
    },
    "params": {
        "required": False,
        "type": dict,
        "donation_required": False,
    },
    "headers": {
        "required": False,
        "type": dict,
        "donation_required": False,
    },
}

DELETESTATUS_PARAMETERS = {
    "date_val": {
        "required": True,
        "description": "Date",
        "type": date,
        "donation_required": False,
        "additional_validators": [validate_delete_status_date],
    },
    "time_val": {
        "required": False,
        "description": "Time",
        "type": time,
        "donation_required": False,
    },
}

ADDSTATUS_PARAMETERS = {
    "d": copy(standard_parameters["d"]),
    "t": copy(standard_parameters["t"]),
    "v1": {
        "required": False,
        "description": "Energy Generation (Wh)",
        "donation_required": False,
        "type": int,
    },
    "v2": {
        "required": False,
        "description": "Power Exporting (W)",
        "donation_required": False,
    },
    "v3": {
        "required": False,
        "description": "Energy Consumption (Wh)",
        "donation_required": False,
        "maxval": 200000,
    },
    "v4": {
        "required": False,
        "description": "Power Importing (W)",
        "donation_required": False,
    },
    "v5": {
        "required": False,
        "description": "Temperature (C)",
        "type": float,
        "donation_required": False,
    },
    "v6": {
        "required": False,
        "description": "Voltage",
        "type": float,
        "donation_required": False,
    },
    "n": {
        "required": False,
        "description": "Net Flag",
        "donation_required": False,
        "format": r"^1$",
    },
    "v7": {
        "required": False,
        "description": "Extended Value 1",
        "donation_required": True,
    },
    "v8": {
        "required": False,
        "description": "Extended Value 2",
        "donation_required": True,
    },
    "v9": {
        "required": False,
        "description": "Extended Value 3",
        "donation_required": True,
    },
    "v10": {
        "required": False,
        "description": "Extended Value 4",
        "donation_required": True,
    },
    "v11": {
        "required": False,
        "description": "Extended Value 5",
        "donation_required": True,
    },
    "v12": {
        "required": False,
        "description": "Extended Value 6",
        "donation_required": True,
    },
    "c1": {
        "required": False,
        "description": "Cumulative Flag",
        "type": int,
        "format": r"[123]{1}",
        "donation_required": False,
    },
    "m1": {
        "required": False,
        "description": "Text Message 1",
        "maxlen": 30,
        "donation_required": True,
    },
    "required_oneof": {"keys": ["v1", "v2", "v3", "v4"]},
}
"""
Cumulative Energy
The following values are valid for the c1 flag.
    1 Both v1 and v3 values are lifetime energy values. Consumption and generation energy is reset to 0 at the start of the day.
    2 Only v1 generation is a lifetime energy value.
    3 Only v3 consumption is a lifetime energy value.
"""

ADDOUTPUT_PARAMETERS = {
    "d": copy(standard_parameters["d"]),
    "g": {
        "required": False,
        "description": "Generated (Wh)",
        "type": int,
        "donation_required": False,
    },
    "e": {
        "required": False,
        "description": "Exported (Wh)",
        "type": int,
        "donation_required": False,
    },
    "pp": {
        "required": False,
        "description": "Peak Power (W)",
        "type": int,
        "donation_required": False,
    },
    "pt": {
        "required": False,
        "description": "Peak Time",
        "format": r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$",
        "type": str,
        "donation_required": False,
    },
    "cd": {
        "required": False,
        "description": "Condition",
        "format": "Fine|Partly Cloudy|Mostly Cloudy|Cloudy|Showers|Snow|Hazy|Fog|Dusty|Frost|Storm",
        "type": str,
        "donation_required": False,
    },
    "tm": {
        "required": False,
        "description": "Min Temp (C)",
        "type": float,
        "donation_required": False,
    },
    "tx": {
        "required": False,
        "description": "Max Temp (C)",
        "type": float,
        "donation_required": False,
    },
    "cm": {
        "required": False,
        "description": "Comments",
        "type": str,
        "donation_required": False,
    },
    "ip": {
        "required": False,
        "description": "Import Peak (Wh)",
        "type": int,
        "donation_required": False,
    },
    "io": {
        "required": False,
        "description": "Import Off Peak (Wh)",
        "type": int,
        "donation_required": False,
    },
    "is": {
        "required": False,
        "description": "Import Shoulder (Wh)",
        "type": int,
        "donation_required": False,
    },
    "ih": {
        "required": False,
        "description": "Import High Shoulder (Wh)",
        "type": int,
        "donation_required": False,
    },
    "c": {
        "required": False,
        "description": "Consumption (Wh)",
        "type": int,
        "donation_required": False,
    },
    "ep": {
        "required": False,
        "description": "Export Peak (Wh)",
        "type": int,
        "donation_required": False,
    },
    "eo": {
        "required": False,
        "description": "Export Off-Peak (Wh)",
        "type": int,
        "donation_required": False,
    },
    "es": {
        "required": False,
        "description": "Export Shoulder (Wh)",
        "type": int,
        "donation_required": False,
    },
    "eh": {
        "required": False,
        "description": "Export High Shoulder (Wh)",
        "type": int,
        "donation_required": False,
    },
}


DELETE_NOTIFICATION_PARAMETERS = {
    "appid": {
        "required": True,
        "type": str,
        "maxlen": 100,
    },
    "alerttype": {
        "required": True,
        "type": int,
        "choices": ALERT_TYPES,
    },
}

REGISTER_NOTIFICATION_PARAMETERS = copy(DELETE_NOTIFICATION_PARAMETERS)
# registering notifications requires a URL
REGISTER_NOTIFICATION_PARAMETERS["url"] = {
    "required": True,
    "type": str,
    "maxlen": 150,
}
