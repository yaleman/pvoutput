import json
import datetime


import src.pvoutput as pvoutput
from src.pvoutput.utils import get_apikey_systemid_from_config


def main():
    apikey, systemid = get_apikey_systemid_from_config()

    pvo = pvoutput.PVOutput(apikey=apikey, systemid=systemid)
    rate_limit = pvo.check_rate_limit()

    print(json.dumps(rate_limit, indent=2))

    reset_datetime = datetime.datetime.fromtimestamp(int(rate_limit['X-Rate-Limit-Reset']), datetime.timezone.utc)
    print(f"{reset_datetime.isoformat()=}")


if __name__ == "__main__":
    main()
