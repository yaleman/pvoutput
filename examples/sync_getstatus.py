import json

from pvoutput import PVOutput


def get_apikey_systemid():
    with open("pvoutput.json", "r", encoding="utf8") as config_file:
        config_data = json.load(config_file)
    return config_data["apikey"], config_data["systemid"]


def main():
    apikey, systemid = get_apikey_systemid()

    pvo = PVOutput(apikey=apikey, systemid=systemid)
    result = pvo.getstatus()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
