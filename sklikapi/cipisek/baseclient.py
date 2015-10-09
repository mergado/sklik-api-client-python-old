import re
import sys
import time
import logging

from warnings import warn
from xmlrpclib import ServerProxy, ProtocolError

from . import exceptions as exc
from .marshalling import marshall_param, marshall_result


_logger = logging.getLogger('sklikapi')


# gevent compatibility
def _create_server_proxy(*args, **kwargs):
    if 'gevent' in sys.modules:
        from gevent.local import local

        class GeventServerProxy(ServerProxy, local):
            """Subclass of :class:`ServerProxy` where each
            instance is used across all greenlets."""
        return GeventServerProxy(*args, **kwargs)

    else:
        return ServerProxy(*args, **kwargs)


class BaseClient(object):
    """Sklik abstract client base class."""

    # How long to wait before re-logging in when session expires (in seconds)
    MALFORMED_SESSION_WAIT = 5

    # How long to wait before retry when IOError/ProtocolError occurs (in seconds)
    ERROR_RETRY_WAIT = 5

    def __init__(self, url, username, password, debug=False, timeout=None,
                 retries=0):
        """Sklik API client. Only "cipisek" API version is supported.

        :param url: Sklik API URL, e.g. https://api.sklik.cz/RPC2
        :param username: Sklik login
        :param password: Sklik user password
        :param debug: Use XML-RPC verbose mode
        :param timeout: Currently not implemented
        :param retries: Number of retries in the case of timeout or
                        ServerError
        """
        self.__session = None
        self.__user_id = None

        if not username or not password:
            raise Exception('Username and password must not be empty')

        self._proxy = _create_server_proxy(url, verbose=debug, allow_none=True)
        self.retries = retries

        versionName, versionNumber = self.get_version()
        _logger.debug('Sklik API version %s %s', versionName, versionNumber)

        if versionName != 'cipisek':
            raise exc.IncompatibleApiVersionError(
                'Only API version "cipisek" is supported.'
            )

        self.__auth = (username, password)
        self._login()

        # load limits
        limits = self.get_limits()
        self.antidos_count = limits['antiDosCallCount']
        self.antidos_interval = limits['antiDosTimeInterval']
        self.batch_limits = limits['batchCallLimits']

    def __del__(self):
        """Logs out."""

        if self.__session is None:
            return

        res = self._proxy.client.logout({'session': self.__session})
        self._check_login_result(res)

    def _login(self):
        res = self._proxy.client.login(*self.__auth)
        self._check_login_result(res)
        self.__session = res["session"]

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

            except exc.InvalidDataError:
                # in fact not-an-error
                raise

            except (ProtocolError, IOError) as e:
                if n >= self.retries:
                    raise
                else:
                    time.sleep(self.ERROR_RETRY_WAIT)
                    _logger.info('%s! Retrying.', str(e))

            except exc.SessionError as e:
                _logger.info('%s! Re-logging in and retrying.', str(e))
                if n >= self.retries:
                    raise
                else:
                    time.sleep(self.MALFORMED_SESSION_WAIT)
                    self._login()

            except exc.SklikApiError as e:
                match = re.match(
                    r'Too many requests. Has to wait ([0-9]+)\[s\].', str(e))
                if match:
                    wait = int(match.group(1)) + 1
                    time.sleep(wait)
                elif n >= self.retries:
                    raise
                else:
                    _logger.info('%s! Retrying.', str(e))

    def _call(self, *args, **kwargs):
        return self._marshall_and_call(*args, **kwargs)

    def _check_login_result(self, res):
        if res["status"] == 400:
            raise exc.ArgumentError(res["statusMessage"], res["problems"])
        elif res["status"] in [301, 401]:
            raise exc.AuthenticationError(res["statusMessage"])
        elif res["status"] != 200:
            raise exc.SklikApiError(res["statusMessage"])

    def _check_result(self, res):
        if "session" in res:
            self.__session = res["session"]

        if res["status"] == 200:
            return
        elif res["status"] == 400:
            raise exc.ArgumentError(res["statusMessage"],
                                    res.get("diagnostics"))
        elif res["status"] == 401:
            raise exc.SessionError(res["statusMessage"])
        elif res["status"] == 403:
            raise exc.AccessError(res["statusMessage"])
        elif res["status"] == 404:
            raise exc.NotFoundError(res["statusMessage"])
        elif res["status"] in [206, 406]:
            raise exc.InvalidDataError(res["status"], res.get("diagnostics"))
        elif res["status"] == 409:
            warn(res["statusMessage"], exc.NoActionWarning)
        else:
            raise exc.SklikApiError(res["statusMessage"])
