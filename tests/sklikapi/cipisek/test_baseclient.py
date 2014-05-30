from sklikapi.cipisek.baseclient import BaseClient
from sklikapi.cipisek.exceptions import IncompatibleApiVersionError, SklikApiError

from . import unittest
from . import only_with_login, get_client, SKLIK_CIPISEK_URL, SKLIK_BAJAJA_URL


class BaseClientTest(unittest.TestCase):

    @only_with_login
    def test_bajaja_check(self):
        with self.assertRaises(IncompatibleApiVersionError):
            c = get_client(BaseClient, SKLIK_BAJAJA_URL)

    @only_with_login
    def test_cipisek_check(self):
        c = get_client(BaseClient, SKLIK_CIPISEK_URL)

    def test_empty_login(self):
        with self.assertRaisesRegexp(Exception, 'Username and password must not be empty'):
            c = BaseClient(SKLIK_CIPISEK_URL, None, 'password')

    def test_empty_password(self):
        with self.assertRaisesRegexp(Exception, 'Username and password must not be empty'):
            c = BaseClient(SKLIK_CIPISEK_URL, 'login@sklik.cz', None)

    @only_with_login
    def test_limits(self):
        c = get_client(BaseClient)
        limits = c.get_limits()
        self.assertEqual(type(limits), dict)
