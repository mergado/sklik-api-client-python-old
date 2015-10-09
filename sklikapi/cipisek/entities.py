from itertools import chain


class Missing(object):
    """Indicates missing value."""

    def __repr__(self):
        return "<Missing>"

    def __str__(self):
        return "Missing"

    # python2
    def __nonzero__(self):
        return False

    # python3
    def __bool__(self):
        return False

Missing = Missing()


class Entity(object):
    """Base class for all sklik entities.

    Can be easily converted to dict just by using `dict(entity)`.
    If you want to include args equal to <Missing>, you can use
    `dict(entity.iterate_all())`
    """

    __slots__ = []

    """Attributes which contains lists of other entities and should be
    automatically converted to instances of entity type. Keys are
    attribute names and values are target class objects
    (or conversion functions).
    """
    _entity_list_attributes = {}

    """Attributes which can be send via entity.update method.
    `None` means all attributes are updatable.
    """
    _updatable_attributes = None

    @classmethod
    def marshall_list(cls, src_list):
        """Converts iterable of dicts/entites to list of instances
        of this class type
        """
        return [
            item if isinstance(item, cls) else cls(item)
            for item in src_list
        ]

    def __init__(self, source=None, **kwargs):
        if source:
            if isinstance(source, type(self)):
                for key, val in source:
                    kwargs[key] = val
            elif isinstance(source, dict):
                kwargs.update(source)

        for key in self._get_slots():
            setattr(self, key, kwargs.get(key, Missing))

        for key, cls in self._entity_list_attributes.items():
            val = getattr(self, key)
            if val:
                setattr(self, key, cls.marshall_list(val))

    def __iter__(self):
        return self.iterate_non_missing()

    def __eq__(self, other):
        for key in self._get_slots():
            if not hasattr(other, key):
                return False
            if getattr(self, key) != getattr(other, key):
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        vals = ['%s=%s' % (key, repr(getattr(self, key)))
                for key in self._get_slots()]
        return '<' + self.__class__.__name__ + ': ' + ', '.join(vals) + '>'

    def __str__(self):
        return repr(self)

    def _get_slots(self):
        """Returns all keys from __slots__  of all parent classes."""
        return chain.from_iterable(getattr(cls, '__slots__', [])
                                   for cls in type(self).__mro__)

    def iterate_all(self):
        """Iterate over all values."""
        return ((key, getattr(self, key))
                for key in self._get_slots())

    def iterate_non_missing(self):
        """Iterate over all values not equal to <Missing>."""
        return ((key, val)
                for (key, val) in self.iterate_all()
                if val != Missing)

    def iterate_updatable(self):
        """Iterate over all values which can be updated."""
        if self._updatable_attributes is None:
            return self.iterate_non_missing()
        return ((key, val)
                for (key, val) in self.iterate_all()
                if val != Missing and key in self._updatable_attributes)

    @property
    def all_fields_missing(self):
        """Whether all fields are equal to <Missing>."""
        for f in self.iterate_non_missing():
            # If at least one field is non-missing, the for cycle
            # will execute its body. We use for, so we don't need to
            # convert the iterator to list
            return False
        else:
            return True


class Ad(Entity):
    """Ad entity. Properties are:
    - `id`
    - `groupId` - AdGroup ID this ad belongs to
    - `requestId` - Chosen id to identify item in response and diagnostics
    - `creative1` - ad headline
    - `creative2` - ad first line
    - `creative3` - ad second line
    - `clickthruText` - displayed URL
    - `clickthruUrl` - target URL
    - `status` - either "active" or "suspend"
    - `createDate`
    - `premiseMode` - for connection with Firmy.cz
    - `premiseId` - for connection with Firmy.cz
    - `deleted`
    - `deletedDate`
    """
    __slots__ = [
        'id', 'groupId', 'requestId', 'creative1', 'creative2', 'creative3',
        'clickthruText', 'clickthruUrl', 'status', 'createDate', 'premiseMode',
        'premiseId', 'deleted', 'deletedDate'
    ]

    _updatable_attributes = [
        'id', 'creative1', 'creative2', 'creative3', 'clickthruText',
        'clickthruUrl', 'status', 'premiseMode', 'premiseId'
    ]

    def is_same_as(self, other):
        """Two ads are considered the same, if creative1-3
        and clickthruText are equal
        """
        return (
            self.creative1 == other.creative1
            and self.creative2 == other.creative2
            and self.creative3 == other.creative3
            and self.clickthruText == other.clickthruText
        )


class Keyword(Entity):
    """Keyword entity.
    """
    __slots__ = [
        'id', 'groupId', 'name', 'matchType', 'deleted', 'status', 'disabled',
        'cpc', 'url', 'createDate', 'minCpc']

    _updatable_attributes = [
        'status', 'cpc', 'url'
    ]


class Group(Entity):
    """Group entity. Properties are:
    - int   campaignId  Campaign id
    - str   name        Group name
    - int   cpc         Group default maximal cost per click
                        (in halers)
    - int   cpcContext  Group default maximal cost per click for
                        context (in halers)
    - int   cpm         (optional) Group cost per thousand impressions,
                        only if is campaign's payment method set as CPM
                        (in halers)
    - str   status      (optional) status of group (default active):
                        active: active state
                        suspend: suspend state
    - int maxUserDailyImpression
                        (optional) Max impressions of group per one
                        user per one day
    - bool deleted      Whether group was removed
    """
    __slots__ = [
        'id', 'campaignId', 'name', 'cpc', 'cpcContext', 'cpm', 'status',
        'maxUserDailyImpression', 'deleted'
    ]

    _updatable_attributes = [
        'id', 'name', 'cpc', 'cpcContext', 'cpm', 'status',
        'maxUserDailyImpression'
    ]


class Vertex(Entity):

    __slots__ = [
        "latitude", "longitude"
    ]


class Region(Entity):

    __slots__ = [
        "type", "predefinedId", "latitude", "longitude", "radius", "vertices"
    ]

    _entity_list_attributes = {
        "vertices": Vertex,
    }


class Campaign(Entity):
    """Campaign entity.
    """
    __slots__ = [
        'id', 'name', 'deleted', 'status', 'dayBudget', 'exhaustedDayBudget',
        'adSelection', 'startDate', 'endDate', 'createDate', 'fulltext',
        'context', 'excludedSearchServices', 'excludedUrls',
        'negativeKeywords', 'userId', 'totalBudget', 'exhaustedTotalBudget',
        'totalClicks', 'exhaustedTotalClicks', 'paymentMethod', 'regions',
        'premiseId'
    ]

    _entity_list_attributes = {
        'negativeKeywords': Keyword,
        'regions': Region,
    }

    _updatable_attributes = [
        'id', 'name', 'status', 'dayBudget', 'startDate',  'endDate',
        'fulltext', 'context', 'excludedSearchServices', 'excludedUrls',
        'negativeKeywords', 'totalBudget', 'totalClicks', 'paymentMethod',
        'regions', 'premiseId'
    ]

    def __init__(self, source=None, **kwargs):
        super(Campaign, self).__init__(source, **kwargs)
        if self.regions is None:
            self.regions = Missing
