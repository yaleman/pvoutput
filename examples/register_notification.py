import src.pvoutput as pvoutput
from src.pvoutput.utils import get_apikey_systemid_from_config


def main():
    apikey, systemid = get_apikey_systemid_from_config()

    pvo = pvoutput.PVOutput(apikey=apikey, systemid=systemid)
    appid = 'my.application.id'
    callback_url = 'http://my.application.com/api/alert.php'
    alert_type = 0
    register_response = pvo.register_notification(appid, callback_url, alert_type)
    print(register_response.text)


if __name__ == "__main__":
    main()
