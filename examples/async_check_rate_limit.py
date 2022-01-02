import datetime

import aiofiles
import aiohttp
import asyncio
import json
from pvoutput.asyncio import PVOutput


async def get_apikey_systemid():
    async with aiofiles.open("pvoutput.json", mode="r", encoding="utf8") as f:
        contents = await f.read()
    config_data = json.loads(contents)
    return config_data["apikey"], config_data["systemid"]


async def main():
    apikey, systemid = await get_apikey_systemid()

    async with aiohttp.ClientSession() as session:
        pvo = PVOutput(apikey=apikey, systemid=systemid, session=session)
        result = await pvo.check_rate_limit()
    print(json.dumps(result, indent=2))

    reset_datetime = datetime.datetime.fromtimestamp(
        int(result["X-Rate-Limit-Reset"]), datetime.timezone.utc
    )
    print(f"{reset_datetime.isoformat()=}")


if __name__ == "__main__":
    asyncio.run(main())
