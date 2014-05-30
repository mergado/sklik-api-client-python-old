from datetime import datetime
from xmlrpclib import DateTime

from sklikapi.cipisek.entities import Entity
from sklikapi.cipisek.marshalling import (marshall_param, marshall_result,
                                          marshall)

from . import unittest


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
            marshalled = marshall_param(data)
            self.assertEqual(marshalled, expected)

    def test_marshall_result(self):
        entity = MockEntity(**self.values)

        tests = [
            (self.values, entity),
            ([1234, self.values, 'abcdef'], [1234, entity, 'abcdef']),
            ((1234, self.values, 'abcdef'), (1234, entity, 'abcdef')),
        ]

        for data, expected in tests:
            marshalled = marshall_result(data, MockEntity)
            self.assertEqual(marshalled, expected)

    def test_marshall_result_keep_dict(self):
        entity = MockEntity(**self.values)

        tests = [
            (self.values, self.values),
            ([1234, self.values, 'abcdef'], [1234, self.values, 'abcdef']),
            ((1234, self.values, 'abcdef'), (1234, self.values, 'abcdef')),
        ]

        for data, expected in tests:
            marshalled = marshall_result(data)
            self.assertEqual(marshalled, expected)

    def test_marshall_generator_param(self):
        data = (self._get_entity() for _ in xrange(2))
        expected = [self.values for _ in xrange(2)]

        marshalled = marshall_param(data)
        self.assertEqual(list(marshalled), expected)

    def test_marshall_generator_result(self):
        data = (self.values for _ in xrange(2))
        expected = [self._get_entity() for _ in xrange(2)]

        marshalled = marshall_result(data, MockEntity)
        self.assertEqual(list(marshalled), expected)

    def test_marshall_generator_function_param(self):
        def data():
            yield self._get_entity()
            yield self._get_entity()
        expected = [self.values for _ in xrange(2)]

        marshalled = marshall_param(data())
        self.assertEqual(list(marshalled), expected)

    def test_marshall_generator_function_result(self):
        def data():
            yield self.values
            yield self.values
        expected = [self._get_entity() for _ in xrange(2)]

        marshalled = marshall_result(data(), MockEntity)
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

    def test_marshall_datetime_result(self):
        py_dt = datetime(2014, 4, 14, 16, 27, 00)
        xml_dt = DateTime('20140414T16:27:00+0200')  # format used by Sklik

        tests = [
            (MockEntity, xml_dt, py_dt),
            (MockEntity, [1234, xml_dt, 'abcdef'], [1234, py_dt, 'abcdef']),
            (MockEntity, (1234, xml_dt, 'abcdef'), (1234, py_dt, 'abcdef')),
            (MockEntity, [{'a': xml_dt}], [MockEntity(a=py_dt)]),
            (None, {'X': [{'a': xml_dt}]}, {'X': [{'a': py_dt}]}),
        ]

        for obj_type, data, expected in tests:
            marshalled = marshall_result(data, obj_type)
            self.assertEqual(marshalled, expected)
