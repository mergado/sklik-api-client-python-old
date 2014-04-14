import sys
import logging
import xmlrpclib

from .exceptions import *


_logger = logging.getLogger('sklikapi')


# gevent compatibility
if 'gevent' in sys.modules:
    from gevent.local import local
    class XmlRpcProxy(ServerProxy, local):
        """Subclass of :class:`ServerProxy` where each instance
        is used across all greenlets."""

else:
    from xmlrpclib import ServerProxy as XmlRpcProxy


class BaseClient(object):
    """Sklik abstract client base class."""

    def __init__(self, url, username, password, debug=False):
        """Sklik API client. Only "cipisek" API version is supported.

        :param url: Sklik API URL, e.g. https://api.sklik.cz/RPC2
        :param username: Sklik login
        :param password: Sklik user password
        :param debug: Use XML-RPC verbose mode
        """
        self.__session = None
        self.__user_id = None

        if not username or not password:
            raise Exception('Username and password must not be empty')

        self.__proxy = XmlRpcProxy(
            url,
            verbose=debug,
            allow_none=True,
            use_datetime=True)

        versionName, versionNumber = self.get_version()
        _logger.debug('Sklik API version %s %s', versionName, versionNumber)

        if versionName != 'cipisek':
            raise IncompatibleApiVersionError(
                'Only API version "cipisek" is supported.'
            )

        res = self.__proxy.client.login(username, password)
        self._check_login_result(res)
        self.__session = res["session"]

    def __del__(self):
        """Logs out."""

        if self.__session == None:
            return

        res = self.__proxy.client.logout(self.__session)
        self._check_login_result(res)

    def work_with_user(self, user_id):
        """Set userID used with all requests."""
        self.__user_id = user_id

    def get_version(self):
        """Returns Sklik API version provided by RPC server.

        :return: tuple (versionName, versionNumber)
        """
        res = self.__proxy.api.version()
        self._check_result(res)
        return res['versionName'], res['versionNumber']

    def get_limits(self):
        """Returns allowed limits for batch operations.

        :return: tuple (versionName, versionNumber)
        """
        res = self.__proxy.api.limits(self._get_user_struct())
        self._check_result(res)
        return dict((x['id'], x['limit']) for x in res['limits'])

    def _get_user_struct(self):
        struct = {'session': self.__session}
        if self.__user_id:
            struct['userId'] = self.__user_id
        return struct

    def _check_login_result(self, res):
        if res["status"] == 400:
            raise ArgumentError(res["statusMessage"], res["errors"])
        elif res["status"] in [301, 401]:
            raise AuthenticationError(res["statusMessage"])
        elif res["status"] != 200:
            raise SklikApiError(res["statusMessage"])

    def _check_result(self, res):
        if "session" in res:
            self.__session = res["session"]
        #endif

        if res["status"] == 200:
            return
        elif res["status"] == 400:
            raise ArgumentError(res["statusMessage"], res.get("errors"))
        elif res["status"] == 401:
            raise SessionError(res["statusMessage"])
        elif res["status"] == 403:
            raise AccessError(res["statusMessage"])
        elif res["status"] == 404:
            raise NotFoundError(res["statusMessage"])
        elif res["status"] == 406:
            raise InvalidDataError(res["status"], res["errors"])
        elif res["status"] == 206:
            warn(res["statusMessage"], SklikApiWarning)
            return
        elif res["status"] == 409:
            warn(res["statusMessage"], NoActionWarning)
        else:
            raise SklikApiError(res["statusMessage"])