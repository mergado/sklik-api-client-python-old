import unittest

from sklikapi.cipisek.entities import Entity
from sklikapi.cipisek.marshalling import (marshall_param, marshall_result,
                                          marshall)

from . import SKLIK_LOGIN, SKLIK_PASSWORD, SKLIK_BAJAJA_URL, SKLIK_CIPISEK_URL


class MockEntity(Entity):
    __slots__ = ['a', 'b', 'c', 'd']


class MarshallingTest(unittest.TestCase):

    # c is missing
    values = dict(a='headline', b=None, d='http://example.com/subpage')

    def _get_entity(self):
        return MockEntity(**self.values)

    def test_marshall_param(self):
        entity = MockEntity(**self.values)

        tests = [
            (entity, self.values),
            ([1234, entity, 'abcdef'], [1234, self.values, 'abcdef']),
            ((1234, entity, 'abcdef'), (1234, self.values, 'abcdef')),
            ({'item': entity, 'not': 'foo'}, {'item': self.values, 'not': 'foo'}),
            ({'item': [entity, 12], 'not': 'foo'}, {'item': [self.values, 12], 'not': 'foo'}),
        ]

        for data, expected in tests:
            marshalled = marshall_param(MockEntity, data)
            self.assertEqual(marshalled, expected)

    def test_marshall_result(self):
        entity = MockEntity(**self.values)

        tests = [
            (self.values, entity),
            ([1234, self.values, 'abcdef'], [1234, entity, 'abcdef']),
            ((1234, self.values, 'abcdef'), (1234, entity, 'abcdef')),
        ]

        for data, expected in tests:
            marshalled = marshall_result(MockEntity, data)
            self.assertEqual(marshalled, expected)

    def test_marshall_generator_param(self):
        data = (self._get_entity() for _ in xrange(2))
        expected = [self.values for _ in xrange(2)]

        marshalled = marshall_param(MockEntity, data)
        self.assertEqual(list(marshalled), expected)

    def test_marshall_generator_result(self):
        data = (self.values for _ in xrange(2))
        expected = [self._get_entity() for _ in xrange(2)]

        marshalled = marshall_result(MockEntity, data)
        self.assertEqual(list(marshalled), expected)

    def test_marshall_generator_function_param(self):
        def data():
            yield self._get_entity()
            yield self._get_entity()
        expected = [self.values for _ in xrange(2)]

        marshalled = marshall_param(MockEntity, data())
        self.assertEqual(list(marshalled), expected)

    def test_marshall_generator_function_result(self):
        def data():
            yield self.values
            yield self.values
        expected = [self._get_entity() for _ in xrange(2)]

        marshalled = marshall_result(MockEntity, data())
        self.assertEqual(list(marshalled), expected)

    def test_marshall_decorator(self):
        data = self._get_entity()

        @marshall(MockEntity)
        def passthru(data):
            """Passthru function."""
            self.assertEqual(self.values, data)
            return data

        self.assertEqual(data, passthru(data))
        self.assertEqual(passthru.__doc__, "Passthru function.")

    def test_marshall_decorator_method(self):
        data = self._get_entity()

        self.assertEqual(data, self.passthru(data, self.values))
        self.assertEqual(self.passthru.__doc__, "Passthru method.")

    @marshall(MockEntity)
    def passthru(self, data, expected):
        """Passthru method."""
        self.assertEqual(expected, data)
        return data
