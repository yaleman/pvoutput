import datetime
import json

from pvoutput import PVOutput


def get_apikey_systemid():
    with open("pvoutput.json", "r", encoding="utf8") as config_file:
        config_data = json.load(config_file)
    return config_data["apikey"], config_data["systemid"]


def main():
    apikey, systemid = get_apikey_systemid()
    pvo = PVOutput(apikey=apikey, systemid=systemid)

    date_val = datetime.date.today()
    time_val = datetime.time(hour=23, minute=45)
    pvo.delete_status(date_val, time_val)


if __name__ == "__main__":
    main()
