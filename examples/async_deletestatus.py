""" delete a status entry """

import asyncio
import datetime
import aiohttp

from utils import get_apikey_systemid
from pvoutput.asyncio import PVOutput


async def main() -> None:
    """main function"""
    configuration = await get_apikey_systemid()

    async with aiohttp.ClientSession() as session:
        pvo = PVOutput(
            apikey=configuration["apikey"],
            systemid=configuration["systemid"],
            session=session,
            donation_made=configuration["donation_made"],
        )

        testdate = datetime.date.today()
        testtime = datetime.time(hour=23, minute=45)
        response = await pvo.delete_status(date_val=testdate, time_val=testtime)
        print(response)


if __name__ == "__main__":
    asyncio.run(main())
