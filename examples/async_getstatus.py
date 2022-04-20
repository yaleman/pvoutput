
""" example pulling a status """

import asyncio
import json
import aiohttp

from utils import get_apikey_systemid
from pvoutput.asyncio import PVOutput


async def main() -> None:
    """main func"""
    configuration = await get_apikey_systemid()

    async with aiohttp.ClientSession() as session:
        pvo = PVOutput(
            apikey=configuration["apikey"],
            systemid=configuration["systemid"],
            session=session,
            donation_made=configuration["donation_made"],
        )
        result = await pvo.getstatus()
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
