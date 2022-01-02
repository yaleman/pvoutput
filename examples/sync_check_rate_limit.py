import datetime

from pvoutput import PVOutput
import json


def get_apikey_systemid():
    with open("pvoutput.json", "r", encoding="utf8") as config_file:
        config_data = json.load(config_file)
    return config_data["apikey"], config_data["systemid"]


def main():
    apikey, systemid = get_apikey_systemid()

    pvo = PVOutput(apikey=apikey, systemid=systemid)
    result = pvo.check_rate_limit()
    print(json.dumps(result, indent=2))

    reset_datetime = datetime.datetime.fromtimestamp(
        int(result["X-Rate-Limit-Reset"]), datetime.timezone.utc
    )
    print(f"{reset_datetime.isoformat()=}")


if __name__ == "__main__":
    main()
