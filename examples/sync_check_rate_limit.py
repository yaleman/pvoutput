""" rate limit check example """
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
    """main cli"""
    configuration = get_apikey_systemid_sync()
    pvo = PVOutput(apikey=configuration["apikey"], systemid=configuration["systemid"])

    result = pvo.check_rate_limit()

    print(json.dumps(result, indent=2))

    reset_datetime = datetime.datetime.fromtimestamp(
        int(result["X-Rate-Limit-Reset"]), datetime.timezone.utc
    )
    print(f"{reset_datetime.isoformat()=}")


if __name__ == "__main__":
    main()
