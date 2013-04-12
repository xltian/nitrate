# -*- coding: utf-8 -*-
#
# Nitrate is copyright 2010 Red Hat, Inc.
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
#   Xuqing Kuang <xkuang@redhat.com>, Chaobin Tang <ctang@redhat.com>

'''
Functions that help access comments
of objects.
'''

# from django
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.comments.models import Comment

# from stdlib
from datetime import datetime

_SITE = Site.objects.get(pk=settings.SITE_ID)

def add_comment(objs, comments, user, submit_date=None):
    '''
    Generic approach adding django.comment for an object.
    params:
        @objs: [model, model,]
        @submit_date: datetime object
    >>> from django.contrib.auth.models import User
    >>> testuser = User.objects.get(email='ctang@redhat.com')
    >>> from tcms.apps.testruns.models import TestCaseRun as Run
    >>> testrun = Run.objects.get(pk=171675)
    >>> comments = 'stupid comments by Homer'
    >>> add_comment([testrun,], comments, testuser)
    '''
    c_type = ContentType.objects.get(model=objs[0].__class__.__name__)
    for obj in objs:
        Comment.objects.create(
            content_type=c_type, site=_SITE,
            object_pk=obj.pk, user=user,
            comment=comments, submit_date=submit_date or datetime.now()
        )

if __name__ == '__main__':
    import doctest
    doctest.testmod()
