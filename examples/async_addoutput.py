import asyncio
import datetime
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

    testdate = datetime.date.today()
    data = {
        "d": testdate.strftime("%Y%m%d"),
        "g": 500,  # Generated (Wh)
        "e": 450,  # Exported (Wh)
    }

    async with aiohttp.ClientSession() as session:
        pvo = PVOutput(apikey=apikey, systemid=systemid, session=session)
        await pvo.addoutput(data)


if __name__ == "__main__":
    asyncio.run(main())
