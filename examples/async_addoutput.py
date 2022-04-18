""" example to push an output value """

import asyncio
import datetime
import json
import os
import sys

import aiofiles
import aiohttp

from pvoutput.asyncio import PVOutput


async def get_apikey_systemid():
    """ loads config """
    if not os.path.exists("pvoutput.json"):
        print("Couldn't find pvoutput.json, quitting!")
        sys.exit(1)
    async with aiofiles.open("pvoutput.json", mode="r", encoding="utf8") as file_handle:
        contents = await file_handle.read()
    config_data = json.loads(contents)
    return config_data["apikey"], config_data["systemid"]

async def main():
    """ main function """
    apikey, systemid = await get_apikey_systemid()

    testdate = datetime.date.today()
    data = {
        "d": testdate.strftime("%Y%m%d"),
        "g": 500,  # Generated (Wh)
        "e": 450,  # Exported (Wh)
    }

    async with aiohttp.ClientSession() as session:
        pvo = PVOutput(apikey=apikey, systemid=systemid, session=session)
        result = await pvo.addoutput(data)
    result.raise_for_status()
    print(f"Status code: {result.status}")
    print(f"Response content: '{await result.text()}'")

if __name__ == "__main__":
    asyncio.run(main())
