import sys
import unittest

try:
    from gevent.local import local
except ImportError:
    pass

from sklikapi.cipisek.baseclient import _create_server_proxy

from . import SKLIK_CIPISEK_URL


@unittest.skipUnless('gevent' in sys.modules, 'Gevent is probably not installed')
class GeventTest(unittest.TestCase):

    def test_gevent_imports(self):
        self.assertIsInstance(_create_server_proxy(SKLIK_CIPISEK_URL), local)
