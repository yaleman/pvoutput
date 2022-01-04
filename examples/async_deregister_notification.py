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

    appid = "my.application.id"
    alerttype = 0

    async with aiohttp.ClientSession() as session:
        pvo = PVOutput(apikey=apikey, systemid=systemid, session=session)

        await pvo.deregister_notification(appid, alerttype)


if __name__ == "__main__":
    asyncio.run(main())
