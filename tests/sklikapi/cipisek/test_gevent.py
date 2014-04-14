import sys
import unittest

try:
    import gevent
except ImportError:
    pass

from sklikapi.cipisek.baseclient import XmlRpcProxy

from . import SKLIK_CIPISEK_URL


@unittest.skipUnless('gevent' in sys.modules, 'Gevent is probably not installed')
class GeventTest(unittest.TestCase):

    def test_gevent_imports(self):
        self.assertIsInstance(XmlRpcProxy(SKLIK_CIPISEK_URL), gevent.local.local)
