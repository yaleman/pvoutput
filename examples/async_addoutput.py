""" example to push an output value """

import asyncio
import datetime

import aiohttp
from utils import get_apikey_systemid

from pvoutput.asyncio import PVOutput


async def main() -> None:
    """main function"""
    configuration = await get_apikey_systemid()

    testdate = datetime.date.today()
    data = {
        "d": testdate.strftime("%Y%m%d"),
        "g": 500,  # Generated (Wh)
        "e": 450,  # Exported (Wh)
    }

    async with aiohttp.ClientSession() as session:
        pvo = PVOutput(
            apikey=configuration["apikey"],
            systemid=configuration["systemid"],
            session=session,
            donation_made=configuration["donation_made"],
        )
        result = await pvo.addoutput(data)
    result.raise_for_status()
    print(f"Status code: {result.status}")
    print(f"Response content: '{await result.text()}'")


if __name__ == "__main__":
    asyncio.run(main())
