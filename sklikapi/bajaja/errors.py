class SklikApiError(Exception):
    """Base Sklik API error exception"""
    pass


class SklikApiWarning(Warning):
    """Base Sklik API warning exception"""
    pass


class IncompatibleApiVersionError(SklikApiError):
    """Sklik API has incompatible version error exception"""
    pass


class NotFoundError(SklikApiError):
    """Sklik API not found error exception"""
    pass


class ArgumentError(SklikApiError):
    """Sklik API argument error exception"""

    __slots__ = ["__errors"]

    def __init__(self, message, errors):
        SklikApiError.__init__(self, message)
        self.__errors = errors

    def errors(self):
        return self.__errors

    def __str__(self):
        s = super(ArgumentError, self).__str__()
        return '; '.join([s] + self.__errors)


class InvalidDataError(SklikApiError):
    """Sklik API invalid data error exception"""

    __slots__ = ["__errors"]

    def __init__(self, message, errors):
        SklikApiError.__init__(self, message)
        self.__errors = errors

    def errors(self):
        return self.__errors

    def __str__(self):
        s = super(InvalidDataError, self).__str__()
        return '; '.join([s] + [e['id'] for e in self.__errors])


class AuthenticationError(SklikApiError):
    """Sklik API authentication error exception"""
    pass


class SessionError(SklikApiError):
    """Sklik API session error exception"""
    pass


class AccessError(SklikApiError):
    """Skik API access error exception"""
    pass


class NoActionWarning(SklikApiWarning):
    """Sklik API no action error exception"""
    pass
