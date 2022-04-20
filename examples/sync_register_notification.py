""" register notification example """
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

    pvo = PVOutput(apikey=configuration["apikey"], systemid=configuration["systemid"])

    appid = "my.application.id"
    url = "http://my.application.com/api/alert.php"
    alerttype = 0
    pvo.register_notification(appid, url, alerttype)


if __name__ == "__main__":
    main()
