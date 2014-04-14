
import sys
from xmlrpclib import ServerProxy

from errors import SklikApiError, AuthenticationError, ArgumentError
from methods import AdMethods, CampaignMethods, ClientMethods, \
                    ConversionMethods, GroupMethods, KeywordMethods, \
                    MiscMethods

# gevent compatibility
def _create_server_proxy(*args, **kwargs):
    if 'gevent' in sys.modules:
        from gevent.local import local
        class GeventServerProxy(ServerProxy, local):
            """Subclass of :class:`ServerProxy` where each instance
            is used across all greenlets."""
        return GeventServerProxy(*args, **kwargs)

    else:
        return ServerProxy(*args, **kwargs)


class Client(AdMethods, CampaignMethods, ClientMethods, \
             ConversionMethods, GroupMethods, KeywordMethods, \
             MiscMethods):
    """Sklik API client class."""

    __slots__ = ["__config", "__proxy", "__session"]

    def __init__(self, config=None):
        """Creates new Sklik API client instance.

        :param config: Sklik API client configuration instance
        """

        self.__session = None

        if not config:
            raise SklikApiError("No config given")

        self.__proxy = _create_server_proxy(
            config.namespace,
            verbose=config.debug,
            allow_none=True)

        res = self.__proxy.client.login(
            config.username,
            config.password)

        if res["status"] == 400:
            raise ArgumentError(res["statusMessage"], res["errors"])
        elif res["status"] == 401:
            raise AuthenticationError(res["statusMessage"])
        elif res["status"] != 200:
            raise SklikApiError(res["statusMessage"])

        self.__session = res["session"]

    def __del__(self):
        """Logs out."""

        if self.__session == None:
            return

        res = self.__proxy.client.logout(self.__session)

        if res["status"] == 400:
            raise ArgumentError(res["statusMessage"], res["errors"])
        elif res["status"] == 401:
            raise AuthenticationError(res["statusMessage"])
        elif res["status"] != 200:
            raise SklikApiError(res["statusMessage"])
