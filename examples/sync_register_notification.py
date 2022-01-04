import json

from pvoutput import PVOutput


def get_apikey_systemid():
    with open("pvoutput.json", "r", encoding="utf8") as config_file:
        config_data = json.load(config_file)
    return config_data["apikey"], config_data["systemid"]


def main():
    apikey, systemid = get_apikey_systemid()

    pvo = PVOutput(apikey=apikey, systemid=systemid)

    appid = "my.application.id"
    url = "http://my.application.com/api/alert.php"
    alerttype = 0
    pvo.register_notification(appid, url, alerttype)


if __name__ == "__main__":
    main()
