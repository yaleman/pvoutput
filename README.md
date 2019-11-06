# pvoutput

PVOutput.org python API module. Works with the R2 [API version spec here](https://pvoutput.org/help.html#api-spec).

Get your API key from [the account page on PVOutput](https://pvoutput.org/account.jsp)

![travis-ci build status](https://travis-ci.org/yaleman/pvoutput.svg?branch=master)

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

Eventually, `pip install pvoutput` should do it. In the interim, for prod just grab the pvoutput directory and include it.

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
