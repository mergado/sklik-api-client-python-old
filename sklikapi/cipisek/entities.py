from itertools import chain


class Missing(object):
    """Indicates missing value."""

    def __repr__(self):
        return "<Missing>"

    def __str__(self):
        return "Missing"

Missing = Missing()


class Entity(object):
    """Base class for all sklik entities.

    Can be easily converted to dict just by using `dict(entity)`.
    If you want to include args equal to <Missing>, you can use
    `dict(entity.iterate_all())`
    """

    __slots__ = []

    def __init__(self, **kwargs):
        for key in self._get_slots():
            setattr(self, key, kwargs.get(key, Missing))

    def __iter__(self):
        return self.iterate_non_missing()

    def __eq__(self, other):
        for key in self._get_slots():
            if not hasattr(other, key):
                return False
            if getattr(self, key) != getattr(other, key):
                return False
        return True

    def  __ne__(self, other):
        return not self.__eq__(other)

    def _get_slots(self):
        """Returns all keys from __slots__  of all parent classes."""
        return chain.from_iterable(getattr(cls, '__slots__', [])
                                   for cls in type(self).__mro__)

    def iterate_all(self):
        """Iterate over all values."""
        return ((key, getattr(self, key, Missing))
                for key in self._get_slots())

    def iterate_non_missing(self):
        """Iterate over all values not equal to <Missing>."""
        return ((key, val)
                for (key, val) in self.iterate_all()
                if val != Missing)


class Ad(Entity):
    __slots__ = ['id', 'groupId', 'creative1', 'creative2', 'creative3',
                 'clickthruText', 'clickthruUrl', 'status', 'createDate',
                 'premiseMode', 'premiseId']
