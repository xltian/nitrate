#!/usr/bin/env python
# @author: chaobin tang <ctang@redhat.com>

'''
Refer to https://bugzilla.redhat.com/show_bug.cgi?id=589633
1. Added a new column for plans named 'owner'
    SQL -
        alter table test_plans add column owner_id mediumint(9) default null;
2. Use plan.latest_text().author for default owner
'''

import os, random
os.environ['DJANGO_SETTINGS_MODULE'] = 'tcms.product_settings'

from tcms.apps.testplans.models import TestPlan

def add_default_owner():
    print 'start updating data ...'
    plans = TestPlan.objects.all()
    for plan in plans:
        doc_manager = None
        try:
            doc_manager = plan.latest_text().author
        except:
            pass
        if doc_manager:
            plan.owner = doc_manager
            plan.save()
    print 'finished updating data'

def verify():
    print 'start verifying ...'
    plans = TestPlan.objects.all()
    sample = random.sample(plans, 10)
    for plan in sample:
        doc_manager = None
        try:
            doc_manager = plan.latest_text().author
        except:
            pass
        assert doc_manager == plan.owner, 'verification failed.'
    print 'verification succeeds'

def main():
    add_default_owner()
    verify()

if __name__ == '__main__':
    main()
