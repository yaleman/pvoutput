from datetime import date, time

import src.pvoutput as pvoutput
from src.pvoutput.utils import get_apikey_systemid_from_config


def main():
    apikey, systemid = get_apikey_systemid_from_config()

    pvo = pvoutput.PVOutput(apikey=apikey, systemid=systemid)
    test_date = date.today()
    test_time = time(hour=20, minute=00)

    delete_status_response = pvo.delete_status(test_date, test_time)
    print(delete_status_response.text)


if __name__ == "__main__":
    main()
