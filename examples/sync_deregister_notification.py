""" example to de-register a notification """
import json
from typing import Any, Dict
from pvoutput import PVOutput


def get_apikey_systemid_sync() -> Dict[str, Any]:
    """non-asyncio config loader"""
    with open("pvoutput.json", "r", encoding="utf8") as config_file:
        config_data: Dict[str, Any] = json.load(config_file)
    return config_data


def main() -> None:
    """main cli"""
    configuration = get_apikey_systemid_sync()

    pvo = PVOutput(
        apikey=configuration["apikey"],
        systemid=configuration["systemid"],
        donation_made=configuration["donation_made"],
    )

    appid = "my.application.id"
    alerttype = 0
    pvo.deregister_notification(appid, alerttype)


if __name__ == "__main__":
    main()
