""" example checking rate limit """

import asyncio
import datetime
import json
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
        result = await pvo.check_rate_limit()
    print(json.dumps(result, indent=2))

    reset_datetime = datetime.datetime.fromtimestamp(
        int(result["X-Rate-Limit-Reset"]), datetime.timezone.utc
    )
    print(f"{reset_datetime.isoformat()=}")


if __name__ == "__main__":
    asyncio.run(main())
