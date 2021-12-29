from datetime import date, time

import src.pvoutput as pvoutput
from src.pvoutput.utils import get_apikey_systemid_from_config


def main():
    apikey, systemid = get_apikey_systemid_from_config()

    pvo = pvoutput.PVOutput(apikey=apikey, systemid=systemid)
    test_date = date.today()
    test_time = time(hour=20, minute=00)
    data = {
        'd': test_date.strftime("%Y%m%d"),
        't': test_time.strftime("%H:%M"),
        'v2': 500,  # power generation
        'v4': 450,  # power consumption
        'v5': 23.5,  # temperature
        'v6': 234.0,  # voltage
    }
    addstatus_response = pvo.addstatus(data)
    print(addstatus_response.text)


if __name__ == "__main__":
    main()
