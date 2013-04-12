#/usr/bin/python

import os

TCMS_SETTINGS_MODULE = 'tcms.product_settings'
os.environ['DJANGO_SETTINGS_MODULE'] = TCMS_SETTINGS_MODULE

from django.db import models

from tcms.apps.testcases.models import TestCasePlan, TestCase
from tcms.apps.testplans.models import TestPlan

_field = models.IntegerField(max_length=11, null=True, blank=True)
_field.contribute_to_class(TestCasePlan, 'sortkey')

def update_sortkey():
    for tc in TestCase.objects.all():
        sk = tc.sortkey
        TestCasePlan.objects.filter(case = tc).update(sortkey = sk)


if __name__ == '__main__':
    update_sortkey()
