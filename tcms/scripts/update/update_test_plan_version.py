# -*- coding: utf-8 -*-
#
# Nitrate is copyright 2010-2012 Red Hat, Inc.
#
# Nitrate is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version. This program is distributed in
# the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranties of TITLE, NON-INFRINGEMENT,
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# The GPL text is available in the file COPYING that accompanies this
# distribution and at <http://www.gnu.org/licenses>.
#
# Authors:
#   Xiangyang Chu <xchu@redhat.com>

'''
Update testplan.default_product_version.
'''
import os, sys, unittest
sys.path.append(os.path.abspath(os.path.join('../../../../', 'nitrate')))
os.environ['DJANGO_SETTINGS_MODULE'] = 'tcms.settings' #NEED TO BE THE ONE THAT USED BY SERVER.

from tcms.apps.management.models import Version
from tcms.apps.testplans.models import TestPlan

class PlanVersionTest(unittest.TestCase):
    def setUp(self):
        self.plans = TestPlan.objects.all()

    def test_versions(self):
        for plan in self.plans:
            self.assertEqual(
                plan.default_product_version,
                plan.product_version.value
            )

def update_version():
    '''
    Set the product_version with get_or_created version object.
    Set the default_product_version with the product_version's value.
    '''
    no_version_TPs = TestPlan.objects.filter(product_version__isnull = True)
    for tp in no_version_TPs:
        new_version, is_created = Version.objects.get_or_create(
            product = tp.product,
            value = tp.default_product_version
        )
        tp.product_version = new_version
        tp.save()

    TPs = TestPlan.objects.all()
    for tp in TPs:
        tp.default_product_version = tp.product_version.value
        tp.save()

def main():
    update_version()
    unittest.main()

if __name__ == '__main__':
    main()
