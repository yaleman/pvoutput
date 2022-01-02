Examples
========

Quickstart
----------
```commandline
pip install pvoutput
python sync_check_rate_limit.py
```

Config File
-----------
The examples in this folder try to read a configuration file with the name `pvoutput.json`.  
An example `pvoutput.example.json` is provided with fake `apikey` and `systemid`.
Copy `pvoutput.example.json` to `pvoutput.json` and put in your own `apikey`and `systemid`.
This should allow you to run all the examples from within this folder.


Async
-----
The async examples in this folder read the configuration file with `aiofiles`.  
To install this library simply run
```commandline
pip install pvoutput aiofiles
python async_check_rate_limit.py
```
You can also replace the async config file reader with the one from the synchronous examples.

To run them
```commandline
python async_check_rate_limit.py
```
