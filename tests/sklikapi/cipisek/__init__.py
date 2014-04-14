import os
from functools import partial

from unittest import skipUnless

SKLIK_LOGIN = os.environ.get('SKLIK_LOGIN')
SKLIK_PASSWORD = os.environ.get('SKLIK_PASSWORD')

SKLIK_BAJAJA_URL = 'https://api.sklik.cz/sandbox/bajaja/RPC2'
SKLIK_CIPISEK_URL = 'https://api.sklik.cz/sandbox/cipisek/RPC2'


only_with_login = partial(skipUnless(
    SKLIK_LOGIN and SKLIK_PASSWORD,
    "SKLIK_LOGIN or SKLIK_PASSWORD environment var not set"
))


def get_client(cls, url=SKLIK_CIPISEK_URL):
    return cls(url, SKLIK_LOGIN, SKLIK_PASSWORD, debug=False)
