import src.pvoutput as pvoutput
from src.pvoutput.utils import get_apikey_systemid_from_config


def main():
    apikey, systemid = get_apikey_systemid_from_config()

    pvo = pvoutput.PVOutput(apikey=apikey, systemid=systemid)
    getstatus_response = pvo.getstatus()
    print(getstatus_response)


if __name__ == "__main__":
    main()
