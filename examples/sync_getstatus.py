""" get status example """

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
    result = pvo.getstatus()
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
