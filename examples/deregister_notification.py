import src.pvoutput as pvoutput
from src.pvoutput.utils import get_apikey_systemid_from_config


def main():
    apikey, systemid = get_apikey_systemid_from_config()

    pvo = pvoutput.PVOutput(apikey=apikey, systemid=systemid)
    appid = 'my.application.id'
    alert_type = 0
    deregister_response = pvo.deregister_notification(appid, alert_type)
    print(deregister_response.text)


if __name__ == "__main__":
    main()
