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
