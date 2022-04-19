""" de-register a notification """

import asyncio
import aiohttp

from utils import get_apikey_systemid
from pvoutput.asyncio import PVOutput


async def main() -> None:
    """main function"""
    configuration = await get_apikey_systemid()

    appid = "my.application.id"
    alerttype = 0

    async with aiohttp.ClientSession() as session:
        pvo = PVOutput(
            apikey=configuration["apikey"],
            systemid=configuration["systemid"],
            session=session,
            donation_made=configuration["donation_made"],
        )
        response = await pvo.deregister_notification(appid, alerttype)
    print(f"{response=}")


if __name__ == "__main__":
    asyncio.run(main())
