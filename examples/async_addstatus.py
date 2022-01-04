import asyncio
import json

import aiofiles
import aiohttp

from pvoutput.asyncio import PVOutput


async def get_apikey_systemid():
    async with aiofiles.open("pvoutput.json", mode="r", encoding="utf8") as f:
        contents = await f.read()
    config_data = json.loads(contents)
    return config_data["apikey"], config_data["systemid"]


async def main():
    apikey, systemid = await get_apikey_systemid()

    data = {
        "v2": 500,  # power generation
        "v4": 450,  # power consumption
        "v5": 23.5,  # temperature
        "v6": 234.0,  # voltage
        "m1": "Testing",  # custom message
    }

    async with aiohttp.ClientSession() as session:
        pvo = PVOutput(apikey=apikey, systemid=systemid, session=session)
        await pvo.addstatus(data)


if __name__ == "__main__":
    asyncio.run(main())
