""" delete status example """
import datetime
import json
from typing import Any, Dict
from pvoutput import PVOutput


def get_apikey_systemid_sync() -> Dict[str, Any]:
    """non-asyncio config loader"""
    with open("pvoutput.json", "r", encoding="utf8") as config_file:
        config_data: Dict[str, Any] = json.load(config_file)
    return config_data


def main() -> None:
    """cli"""
    configuration = get_apikey_systemid_sync()
    pvo = PVOutput(
        apikey=configuration["apikey"],
        systemid=configuration["systemid"],
        donation_made=configuration["donation_made"],
    )

    date_val = datetime.date.today()
    time_val = datetime.time(hour=23, minute=45)
    response = pvo.delete_status(date_val, time_val)
    print(response)


if __name__ == "__main__":
    main()
