#!/usr/bin/env python
# @author: chaobin tang <ctang@redhat.com>
# Added on 18/05/2011

'''
A script that is supposed to run once
to add default groups defined in product_settings
to all existing users.
'''
import os, random
os.environ['DJANGO_SETTINGS_MODULE'] = 'tcms.product_settings'

from django.contrib.auth.models import User, Group
from django.conf import settings

def update():
    print "Starting to update user's group ..."
    users = User.objects.all()
    print "%s users to be updated" % users.count()
    default_groups = Group.objects.filter(name__in=settings.DEFAULT_GROUPS)
    print "%s groups to be added" % default_groups.count()
    for user in users:
        for grp in default_groups:
            user.groups.add(grp)
    print "Done Updating"

def verify():
    print "Starting to verify ..."
    users = User.objects.all()
    default_groups = set(settings.DEFAULT_GROUPS)
    for i in range(10):
        user = random.choice(users)
        user_groups = set([g['name'] for g in user.groups.values('name')])
        assert default_groups.issubset(user_groups), 'Verification failed.'
    raise SystemExit("Successfully Updated!")

if __name__ == '__main__':
    update()
    verify()
