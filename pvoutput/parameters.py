from copy import copy

standard_parameters = {
    "d": {
        "required": True,
        "description": "Date",
        "format": "[0-9]{8}",
        "type": str,
        "donation_required": False,
    },
    "t": {
        "required": True,
        "description": "Time",
        "format": "[12]{0,1}[0-9]{1}:[1-5]{0,1}[0-9]{1}",
        "type": str,
        "donation_required": False,
    },  # TODO: the validator is terrible
}

DELETESTATUS_PARAMETERS = {
    "d": copy(standard_parameters["d"]), 
    "t": copy(standard_parameters["t"]),
    }
DELETESTATUS_PARAMETERS["t"]["required"] = False  # isn't required if 'd' is set

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
        "format": "^1$",
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
        "format": "[123]{1}",
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
