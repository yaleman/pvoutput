""" shared utils for examples """

import json
import os
import sys
from typing import Any, Dict

import aiofiles


async def get_apikey_systemid() -> Dict[str, Any]:
    """loads config"""
    if not os.path.exists("pvoutput.json"):
        print("Couldn't find pvoutput.json, quitting!")
        sys.exit(1)
    async with aiofiles.open("pvoutput.json", mode="r", encoding="utf8") as file_handle:
        contents = await file_handle.read()
    config_data: Dict[str, Any] = json.loads(contents)
    return config_data
