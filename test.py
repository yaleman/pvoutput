#!/usr/bin/env python3

""" random test things """

import os
import sys
import json
from datetime import date, time

from pvoutput import PVOutput

if not os.path.exists(os.path.expanduser("~/.config/pvoutput.json")):
    print("Failed to find config file")
    sys.exit(1)

with open(
    os.path.expanduser("~/.config/pvoutput.json"), "r", encoding="utf8"
) as config_file:
    config = json.load(config_file)

pvo = PVOutput(
    apikey=config.get("apikey"), systemid=config.get("systemid"), donation_made=True
)

# print("testign check_rate_limit()")
# print(json.dumps(pvo.check_rate_limit(), indent=2))

testdate = date.today()
testtime = time(hour=20, minute=00)
data = {
    "d": testdate.strftime("%Y%m%d"),
    "t": testtime.strftime("%H:%M"),
    "v2": 500,  # power generation
    "v4": 450,  # power consumption
    "v5": 23.5,  # temperature
    "v6": 234.0,  # voltage
    "m1": "Testing",  # custom message
}
# print("Testing addstatus for 20:00")
# print(pvo.addstatus(data).text)

# print("Testing delete_status for 20:00")
# print(pvo.delete_status(date_val=testdate, time_val=testtime).text)

print("Getstatus")
print(pvo.getstatus())
print("Rate limit")
print(pvo.check_rate_limit())
