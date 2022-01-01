# pvoutput

PVOutput.org python API module. Works with the R2 [API version spec here](https://pvoutput.org/help.html#api-spec).

Get your API key from [the account page on PVOutput](https://pvoutput.org/account.jsp)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
# Example usage

    > from pvoutput import PVOutput
    > import json
    > apikey = 'aaaaaabbbbbbccccccddddddeeeeeeffffffgggg'
    > systemid = 12345
    > pvo = PVOutput(apikey=apikey, systemid=systemid)
    > print(json.dumps(pvo.check_rate_limit(), indent=2))
    {
    "X-Rate-Limit-Remaining": "271",
    "X-Rate-Limit-Limit": "300",
    "X-Rate-Limit-Reset": "1570597200"
    }

# Installing

## Prod-ish usage

`python3 -m pip install pvoutput` to install

* `pipenv install -r requirements.txt` or
* `pip install -r requirements.txt`

## Dev

Either:

* `pipenv install -r requirements-dev.txt` or
* `pip install -r requirements-dev.txt`

# Testing

I'm using `pytest` as best I can. `pipenv install --dev; pipenv run pytest` should do it.

# License

MIT License (see `LICENSE`), don't use this for anything you care about - I don't provide a warranty at all, and it'll likely steal your socks and underfeed your dog.

# Changelog

* 0.0.1 Initial version
* 0.0.2 2019-10-12 Fixed some bugs
* 0.0.3 2019-10-13 Added PVOutput.getstatus() which returns the current status as a dict
* 0.0.4 2019-11-05 Code cleanup using sonarqube, added an error check for registernotification
* 0.0.5 Asyncio things
* 0.0.6 I broke the build when uploading to pypi, fixed in 0.0.7.
* 0.0.7 2021-12-27 [#117](https://github.com/yaleman/pvoutput/issues/117) fix for getstatus issues
* 0.0.8 2022-01-02 @cheops did great work cleaning up a lot of my mess, and testing is much better.