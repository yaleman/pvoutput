""" addstatus example """
import json
from typing import Any, Dict
from pvoutput import PVOutput


def get_apikey_systemid_sync() -> Dict[str, Any]:
    """non-asyncio config loader"""
    with open("pvoutput.json", encoding="utf8") as config_file:
        config_data: Dict[str, Any] = json.load(config_file)
    return config_data


def main() -> None:
    """main cli"""
    configuration = get_apikey_systemid_sync()
    data = {
        "v2": 500,  # power generation
        "v4": 450,  # power consumption
        "v5": 23.5,  # temperature
        "v6": 234.0,  # voltage
        "m1": "Testing",  # custom message
    }
    pvo = PVOutput(
        apikey=configuration["apikey"],
        systemid=configuration["systemid"],
        donation_made=configuration["donation_made"],
    )
    try:
        response = pvo.addstatus(data)
        print(response)
    except Exception as err: #pylint: disable=broad-except
        print(f"{err=}")
        # print(response.request.method)


if __name__ == "__main__":
    main()
