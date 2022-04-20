""" synchronous addoutput example """
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
    """main func"""
    configuration = get_apikey_systemid_sync()
    pvo = PVOutput(
        apikey=configuration["apikey"],
        systemid=configuration["systemid"],
        donation_made=configuration["donation_made"],
    )

    testdate = datetime.date.today()
    data = {
        "d": testdate.strftime("%Y%m%d"),
        "g": 500,  # Generated (Wh)
        "e": 450,  # Exported (Wh)
    }
    print("Adding output")
    result = pvo.addoutput(data)
    print(f"Status code: {result.status_code}")
    print(f"Response content: '{result.text}'")


if __name__ == "__main__":
    main()
