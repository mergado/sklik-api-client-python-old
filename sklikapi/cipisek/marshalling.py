from types import GeneratorType
from itertools import imap
from functools import partial, wraps

from .entities import Missing


def marshall_param(obj_type, data):
    if isinstance(data, obj_type):
        return dict((k, marshall_param(obj_type, v))
                    for (k, v) in data)

    elif isinstance(data, dict):
        return dict((key, marshall_param(obj_type, value))
                    for key, value in data.iteritems())

    elif isinstance(data, list):
        return map(partial(marshall_param, obj_type), data)

    elif isinstance(data, tuple):
        return tuple(map(partial(marshall_param, obj_type), data))

    elif isinstance(data, GeneratorType):
        return imap(partial(marshall_param, obj_type), data)

    else:
        return data


def marshall_result(obj_type, data):
    if isinstance(data, dict):
        kwargs = dict((k, marshall_result(obj_type, v))
                      for (k, v) in data.iteritems())
        return obj_type(**kwargs)

    elif isinstance(data, list):
        return map(partial(marshall_result, obj_type), data)

    elif isinstance(data, tuple):
        return tuple(map(partial(marshall_result, obj_type), data))

    else:
        return data


def marshall(obj_type):
    def wrapper(func):
        @wraps(func)
        def marshaller(*args, **kwargs):
            args = marshall_param(obj_type, args)
            kwargs = marshall_param(obj_type, kwargs)
            return marshall_result(obj_type, func(*args, **kwargs))
        return marshaller
    return wrapper
