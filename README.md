# Sklik.cz API Python client

Sklik.cz is a pay-per-click advertising system, operated by Seznam.cz, a.s.
This is a Python library (module) for easier access to the Sklik.cz API.

This library is based on the Python client written by Eduard Veleba for the second version of Sklik API Bajaja. This version contains both, the client for the old version Bajaja and the client for the new third version named Cipisek.

Sklik.cz API homepage and documentation: [http://api.sklik.cz/](http://api.sklik.cz/)

## Installation

To install, run the following command from the top-level package directory.

```bash
$ python setup.py install
```

## Getting Started

The first thing is to instantiate the Client class (note that this immediately creates connection with Sklik API, i.e. if the credentials are invalid, the instantiation fails with `AuthenticationError`).

```python
from sklikapi.cipisek import Client

client = Client('https://api.sklik.cz/cipisek/RPC2/',
                'username@example.com',
                'password')
```

Now you can create/get resources.

```python
client.get_ads(<ads_id>)
```
