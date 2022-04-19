""" pvoutput example to add a status entry """

import asyncio

import aiohttp
from utils import get_apikey_systemid
from pvoutput.asyncio import PVOutput


async def main() -> None:
    """main function"""
    configuration = await get_apikey_systemid()

    data = {
        "v2": 500,  # power generation
        "v4": 450,  # power consumption
        "v5": 23.5,  # temperature
        "v6": 234.0,  # voltage
        "m1": "Testing",  # custom message
    }

    async with aiohttp.ClientSession() as session:
        pvo = PVOutput(
            apikey=configuration["apikey"],
            systemid=configuration["systemid"],
            session=session,
            donation_made=configuration["donation_made"],
        )
        response = await pvo.addstatus(data)
        print(f"{response=}")


if __name__ == "__main__":
    asyncio.run(main())
