""" example registering a callback """
import asyncio

import aiohttp
from utils import get_apikey_systemid
from pvoutput.asyncio import PVOutput


async def main() -> None:
    """main func"""
    configuration = await get_apikey_systemid()

    appid = "my.application.id"
    url = "http://my.application.com/api/alert.php"
    alerttype = 0

    async with aiohttp.ClientSession() as session:
        pvo = PVOutput(
            apikey=configuration["apikey"],
            systemid=configuration["systemid"],
            session=session,
            donation_made=configuration["donation_made"],
        )

        await pvo.register_notification(appid, url, alerttype)


if __name__ == "__main__":
    asyncio.run(main())
