import json

from pvoutput import PVOutput


def get_apikey_systemid():
    with open("pvoutput.json", "r", encoding="utf8") as config_file:
        config_data = json.load(config_file)
    return config_data["apikey"], config_data["systemid"]


def main():
    apikey, systemid = get_apikey_systemid()
    pvo = PVOutput(apikey=apikey, systemid=systemid)

    data = {
        "v2": 500,  # power generation
        "v4": 450,  # power consumption
        "v5": 23.5,  # temperature
        "v6": 234.0,  # voltage
        "m1": "Testing",  # custom message
    }
    pvo.addstatus(data)


if __name__ == "__main__":
    main()
