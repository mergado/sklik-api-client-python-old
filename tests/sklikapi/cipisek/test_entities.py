from sklikapi.cipisek.entities import Entity, Missing

from . import unittest

class MockEntity(Entity):
    __slots__ = ['a', 'b', 'c', 'd']


class EntityTest(unittest.TestCase):

    # c is missing
    values = dict(a='headline', b=None, d='http://example.com/subpage')

    def _get_entity(self):
        return MockEntity(**self.values)

    def test_create_entity(self):
        entity = MockEntity(**self.values)
        self.assertEqual(entity.a, self.values['a'])
        self.assertEqual(entity.b, self.values['b'])
        self.assertEqual(entity.c, Missing)
        self.assertEqual(entity.d, self.values['d'])

    def test_entity_to_dict(self):
        entity = MockEntity(**self.values)
        self.assertEqual(self.values, dict(entity))
