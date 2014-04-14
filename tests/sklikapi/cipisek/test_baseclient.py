import unittest

from sklikapi.cipisek.baseclient import BaseClient
from sklikapi.cipisek.exceptions import IncompatibleApiVersionError, SklikApiError

from . import SKLIK_LOGIN, SKLIK_PASSWORD, SKLIK_BAJAJA_URL, SKLIK_CIPISEK_URL


login_provided = SKLIK_LOGIN and SKLIK_PASSWORD


class BaseClientTest(unittest.TestCase):

    def _get_client(self):
        return BaseClient(SKLIK_CIPISEK_URL, SKLIK_LOGIN, SKLIK_PASSWORD)

    @unittest.skipUnless(login_provided, "No login data provided")
    def test_bajaja_check(self):
        with self.assertRaises(IncompatibleApiVersionError):
            c = BaseClient(SKLIK_BAJAJA_URL, SKLIK_LOGIN, SKLIK_PASSWORD)

    @unittest.skipUnless(login_provided, "No login data provided")
    def test_cipisek_check(self):
        c = BaseClient(SKLIK_CIPISEK_URL, SKLIK_LOGIN, SKLIK_PASSWORD)

    def test_empty_login(self):
        with self.assertRaisesRegexp(Exception, 'Username and password must not be empty'):
            c = BaseClient(SKLIK_CIPISEK_URL, None, 'password')

    def test_empty_password(self):
        with self.assertRaisesRegexp(Exception, 'Username and password must not be empty'):
            c = BaseClient(SKLIK_CIPISEK_URL, 'login@sklik.cz', None)

    @unittest.skipUnless(login_provided, "No login data provided")
    def test_limits(self):
        c = self._get_client()
        limits = c.get_limits()
        self.assertEqual(type(limits), dict)
