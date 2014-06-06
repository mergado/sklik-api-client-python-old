import sys
import errno
import logging
from httplib import HTTPSConnection, HTTPS
from warnings import warn
from xmlrpclib import ServerProxy, Transport

from .exceptions import *
from .marshalling import marshall_param, marshall_result
from .utils import split_every


_logger = logging.getLogger('sklikapi')


class TimeoutHTTPSConnection(HTTPSConnection):

   def connect(self):
       HTTPSConnection.connect(self)
       self.sock.settimeout(self.timeout)


class TimeoutHTTPS(HTTPS):

   _connection_class = TimeoutHTTPSConnection

   def set_timeout(self, timeout):
       self._conn.timeout = timeout


class TimeoutTransport(Transport):

    def __init__(self, timeout=10, *args, **kwargs):
        self.timeout = timeout
        Transport.__init__(self, *args, **kwargs)

    def make_connection(self, host):
        conn = TimeoutHTTPS(host)
        conn.set_timeout(self.timeout)
        return conn

class TimeoutServerProxy(ServerProxy):

    def __init__(self, uri, timeout=10, *args, **kwargs):
        kwargs['transport'] = TimeoutTransport(
            timeout=timeout,
            use_datetime=kwargs.get('use_datetime', 0)
        )
        ServerProxy.__init__(self, uri, *args, **kwargs)


# gevent compatibility
def _create_server_proxy(*args, **kwargs):
    if 'gevent' in sys.modules:
        from gevent.local import local
        class GeventServerProxy(TimeoutServerProxy, local):
            """Subclass of :class:`TimeoutServerProxy` where each
            instance is used across all greenlets."""
        return GeventServerProxy(*args, **kwargs)

    else:
        return TimeoutServerProxy(*args, **kwargs)


class BaseClient(object):
    """Sklik abstract client base class."""

    def __init__(self, url, username, password, debug=False, timeout=None,
                 retries=0):
        """Sklik API client. Only "cipisek" API version is supported.

        :param url: Sklik API URL, e.g. https://api.sklik.cz/RPC2
        :param username: Sklik login
        :param password: Sklik user password
        :param debug: Use XML-RPC verbose mode
        :param timeout: Timeout (in seconds) for XML-RPC calls
        :param retries: Number of retries in the case of timeout or
                        ServerError
        """
        self.__session = None
        self.__user_id = None

        if not username or not password:
            raise Exception('Username and password must not be empty')

        self._proxy = _create_server_proxy(url, verbose=debug, allow_none=True,
                                           timeout=timeout)
        self.retries = retries

        versionName, versionNumber = self.get_version()
        _logger.debug('Sklik API version %s %s', versionName, versionNumber)

        if versionName != 'cipisek':
            raise IncompatibleApiVersionError(
                'Only API version "cipisek" is supported.'
            )

        res = self._proxy.client.login(username, password)
        self._check_login_result(res)
        self.__session = res["session"]

        # load limits
        limits = self.get_limits()
        self.antidos_count = limits['antiDosCallCount']
        self.antidos_interval = limits['antiDosTimeInterval']
        self.batch_limits = limits['batchCallLimits']

    def __del__(self):
        """Logs out."""

        if self.__session == None:
            return

        res = self._proxy.client.logout({'session': self.__session})
        self._check_login_result(res)

    def get_batch_limit(self, operation):
        if operation in self.batch_limits:
            return self.batch_limits[operation]
        else:
            resource, op = operation.split('.')
            return self.batch_limits.get('global.' + op)

    def work_with_user(self, user_id):
        """Set userID used with all requests."""
        self.__user_id = user_id

    def get_version(self):
        """Returns Sklik API version provided by RPC server.

        :return: tuple (versionName, versionNumber)
        """
        res = self._proxy.api.version()
        self._check_result(res)
        return res['versionName'], res['versionNumber']

    def get_limits(self):
        """Returns allowed limits for batch operations.

        :return: tuple (versionName, versionNumber)
        """
        res = self._proxy.api.limits(self._get_user_struct())
        self._check_result(res)

        limits = res['limits']
        limits['batchCallLimits'] = dict((x['name'], x['limit'])
                                         for x in res['batchCallLimits'])
        return limits

    def _get_user_struct(self):
        struct = {'session': self.__session}
        if self.__user_id:
            struct['userId'] = self.__user_id
        return struct

    def _marshall_and_call(self, method, *args, **kwargs):
        args = (self._get_user_struct(),) + marshall_param(args)
        kwargs = marshall_param(kwargs)
        result = marshall_result(self._call_and_retry(method, *args, **kwargs))
        return result

    def _call_and_retry(self, method, *args, **kwargs):
        method = getattr(self._proxy, method)
        for n in xrange(self.retries + 1):
            try:
                result = method(*args, **kwargs)
                self._check_result(result)
                return result

            except IOError as e:
                if 'timed out' in e.args[0]:
                    if n > self.retries:
                        raise
                    else:
                        _logger.info('Timeout! Retrying.')
                else:
                    raise

            except SklikApiError as e:
                if n > self.retries:
                    raise
                else:
                    _logger.info('%s! Retrying.', str(e))

    def _call(self, *args, **kwargs):
        return self._marshall_and_call(*args, **kwargs)

    def _check_login_result(self, res):
        if res["status"] == 400:
            raise ArgumentError(res["statusMessage"], res["problems"])
        elif res["status"] in [301, 401]:
            raise AuthenticationError(res["statusMessage"])
        elif res["status"] != 200:
            raise SklikApiError(res["statusMessage"])

    def _check_result(self, res):
        if "session" in res:
            self.__session = res["session"]

        if res["status"] == 200:
            return
        elif res["status"] == 400:
            raise ArgumentError(res["statusMessage"], res.get("diagnostics"))
        elif res["status"] == 401:
            raise SessionError(res["statusMessage"])
        elif res["status"] == 403:
            raise AccessError(res["statusMessage"])
        elif res["status"] == 404:
            raise NotFoundError(res["statusMessage"])
        elif res["status"] == 406:
            raise InvalidDataError(res["status"], res.get("diagnostics"))
        elif res["status"] == 206:
            warn(res["statusMessage"], SklikApiWarning)
            return
        elif res["status"] == 409:
            warn(res["statusMessage"], NoActionWarning)
        else:
            raise SklikApiError(res["statusMessage"])
