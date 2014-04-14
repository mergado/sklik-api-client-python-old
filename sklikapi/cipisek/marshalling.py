from time import strptime
from types import GeneratorType
from datetime import datetime
from itertools import imap
from functools import partial, wraps
from xmlrpclib import DateTime

from .entities import Missing, Entity


def marshall_param(data):
    """Converts all `Entity` instances to dicts, recursively.
    Dicts, lists, and tuples are kept, generators are wrapped by
    `itertools.imap`, `datetime.datetime` objects are converted to
    `xmlrpclib.DateTime`. Other data types are left as-is.
    """

    if isinstance(data, Entity):
        return dict((k, marshall_param(v))
                    for (k, v) in data)

    elif isinstance(data, dict):
        return dict((key, marshall_param(value))
                    for key, value in data.iteritems())

    elif isinstance(data, list):
        return map(marshall_param, data)

    elif isinstance(data, tuple):
        return tuple(map(marshall_param, data))

    elif isinstance(data, GeneratorType):
        return imap(marshall_param, data)

    elif isinstance(data, datetime):
        return DateTime(data)

    else:
        return data


def marshall_result(data, obj_type=None):
    """
    Lists and tuples are kept, generators are wrapped by
    `itertools.imap`, `xmlrpclib.DateTime` objects are converted to
    `datetime.datetime`. Dicts are kept unless `obj_type` is set, in
    which case dicts are converted to `obj_type` instances.
    Other data types are left as-is.
    """

    recursion = lambda data: marshall_result(data, obj_type)

    if obj_type and isinstance(data, dict):
        kwargs = dict((k, recursion(v))
                      for (k, v) in data.iteritems())
        return obj_type(**kwargs)

    elif isinstance(data, dict):
        return dict((k, recursion(v))
                      for (k, v) in data.iteritems())

    elif isinstance(data, list):
        return map(recursion, data)

    elif isinstance(data, tuple):
        return tuple(map(recursion, data))

    elif isinstance(data, GeneratorType):
        return imap(recursion, data)

    elif isinstance(data, DateTime):
        return datetime(*strptime(data.value[:-5], "%Y%m%dT%H:%M:%S")[:6])

    else:
        return data


def marshall(obj_type=None):
    """Decorator which automatically marshalles arguments and function
    result using `marshall_param` and `marshall_result` functions.
    """

    def wrapper(func):
        @wraps(func)
        def marshaller(*args, **kwargs):
            args = marshall_param(args)
            kwargs = marshall_param(kwargs)
            return marshall_result(func(*args, **kwargs), obj_type)
        return marshaller
    return wrapper
