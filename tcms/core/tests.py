# -*- coding: utf-8 -*-

import unittest

from tcms.apps.testcases.models import TestCase

class TestUtilsXmlrpc(unittest.TestCase):

    def setUp(self):
        self.testcase_with_default_tester_null = TestCase.objects.extra(
            where=['default_tester_id is null'])[0:1].get()
        self.testcase_with_default_tester_0 = TestCase.objects.extra(
            where=['default_tester_id = 0'])[0:1].get()
        self.testcase_with_valid_default_tester = TestCase.objects.filter(
            default_tester__isnull=False)[0:1].get()

    def test_serialize_model_foreignkey(self):
        '''Testing whether the foreign key is serialized properly

        If foreign key has related object, the field should be serialized with
        the correct value.
        If there is no related object with the foreign key, both the field and
        the related object retrived via the relationship are set to None.
        '''

        from tcms.core.utils.xmlrpc import XMLRPCSerializer

        s = XMLRPCSerializer(model = self.testcase_with_default_tester_null)
        result = s.serialize_model()
        self.assertEqual(result['default_tester'], None)
        self.assertEqual(result['default_tester_id'], None)

        s = XMLRPCSerializer(model = self.testcase_with_default_tester_0)
        result = s.serialize_model()
        self.assertEqual(result['default_tester'], None)
        self.assertEqual(result['default_tester_id'], None)

        s = XMLRPCSerializer(model = self.testcase_with_valid_default_tester)
        result = s.serialize_model()
        self.assertNotEqual(result['default_tester'], None)
        self.assertNotEqual(result['default_tester_id'], None)

if __name__ == '__main__':
    unittest.main()
