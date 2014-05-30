import os
from functools import partial

try:
    import unittest2 as unittest
except ImportError:
    import unittest

if not hasattr(unittest, 'skipUnless'):
    raise Exception('Please install unittest2 package (unittest.skipUnless attribute is missing)')

SKLIK_LOGIN = os.environ.get('SKLIK_LOGIN')
SKLIK_PASSWORD = os.environ.get('SKLIK_PASSWORD')

SKLIK_BAJAJA_URL = 'https://api.sklik.cz/sandbox/bajaja/RPC2'
SKLIK_CIPISEK_URL = 'https://api.sklik.cz/sandbox/cipisek/RPC2'


only_with_login = partial(unittest.skipUnless(
    SKLIK_LOGIN and SKLIK_PASSWORD,
    "SKLIK_LOGIN or SKLIK_PASSWORD environment var not set"
))


def get_client(cls, url=SKLIK_CIPISEK_URL):
    return cls(url, SKLIK_LOGIN, SKLIK_PASSWORD, debug=False)
