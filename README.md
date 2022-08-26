# pvoutput

PVOutput.org python API module. Works with the R2 [API version spec here](https://pvoutput.org/help.html#api-spec).

Get your API key from [the account page on PVOutput](https://pvoutput.org/account.jsp)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
# Example usage

Here's a quick code example:

```python
    from pvoutput import PVOutput
    import json
    apikey = 'aaaaaabbbbbbccccccddddddeeeeeeffffffgggg'
    systemid = 12345
    pvo = PVOutput(apikey=apikey, systemid=systemid)
    print(json.dumps(pvo.check_rate_limit(), indent=2))
```
Will give you output like this:
```
    {
        "X-Rate-Limit-Remaining": "271",
        "X-Rate-Limit-Limit": "300",
        "X-Rate-Limit-Reset": "1570597200"
    }
```

There are more example code snippets in the [examples](examples/) directory.

# Installing

## Prod-ish usage

`python -m pip install pvoutput` to install from pypi

## Dev Install Things

```shell
python -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip flit
python -m flit install
```

# Input validation

This is handled by the `pvoutput.base.PVOutputBase.validate_data` function.

It expects the input data and a dict of configuration parameters, which are described in the table below:

| Field name | Required | Valid Types | Description |
| --- |  --- | --- | --- |
| `type` | Yes | `Any` | This is a python type object to match against the field type. |
| `required` | No | `bool` | This defines if the field is required. |
| `description` | No | `Any` | This is currently unused, but typically holds the description from the PVOutput API Docs |
| `donation_required` | No | `bool` | If set to true, and the user's not donated, it'll throw a `DonationRequired` exception if the user tries to use functionality that requires them to have donated. It's a whole thing. |
| `maxlen` | No | `int` | Maximum length of the field. ie. `if len(field) > maxlen: raise ValueError` |
| `maxval` | No | `int` | Maximum value of the field. |
| `minval` | No | `int` | Minimum value of the field. |
| `additional_validators` | No | `List[function]` | A list of functions to run against the field, which should throw exceptions if something's wrong. |

An example configuration

```
"date_val": {
    "required": True,
    "description": "Date",
    "type": date,
    "donation_required": False,
    "additional_validators" : [
        validate_delete_status_date
    ]
}
```

# Contributing / Testing

`pylint`, `black` and `mypy` should all pass before submitting a PR.

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
* 0.0.10 2022-08-27 Added explicit timeouts to HTTP connections in the synchronous client.
* 0.0.11 2022-08-27 Added explicit timeouts to HTTP connections in the aiohttp client.