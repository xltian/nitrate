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
#   Xuqing Kuang <xkuang@redhat.com>

from django.db import models

from tcms.core.models import TCMSContentTypeBaseModel

class Profiles(models.Model):
    userid = models.AutoField(primary_key=True)
    login_name = models.CharField(max_length=255, unique=True)
    cryptpassword = models.CharField(max_length=128, blank=True)
    realname = models.CharField(max_length=255)
    disabledtext = models.TextField()
    disable_mail = models.IntegerField(max_length=4)
    mybugslink = models.IntegerField(max_length=4)
    extern_id = models.IntegerField(max_length=4, blank=True)
    class Meta:
        db_table = u'profiles'

    def get_groups(self):
        q = UserGroupMap.objects.filter(user__userid = self.userid)
        q = q.select_related()
        groups = [assoc.group for assoc in q.all()]
        return groups

    def add_testopia_permissions(self):
        """
        Emulate Testopia permissions for a freshly-created account.

        Add rows to test_plan_permissions for any of the regexps that this
        account matches.
        """
        import re
        from tcms.apps.testplans.models import TestPlanPermission, TestPlanPermissionsRegexp
        for perm_regexp in TestPlanPermissionsRegexp.objects.all():
            if re.match(perm_regexp.user_regexp, self.login_name):
                TestPlanPermission.objects.create(
                    userid = self.userid,
                    plan_id = perm_regexp.plan_id,
                    permissions = perm_regexp.permissions,
                    grant_type = 2 # GRANT_REGEXP
                )

class Groups(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    description = models.TextField()
    isbuggroup = models.IntegerField()
    userregexp = models.TextField()
    isactive = models.IntegerField()
    class Meta:
        db_table = u'groups'

class UserGroupMap(models.Model):
    user = models.ForeignKey(Profiles, primary_key=True) # user_id
    # (actually has two primary keys)
    group = models.ForeignKey(Groups) # group_id
    isbless = models.IntegerField()
    grant_type = models.IntegerField()
    class Meta:
        db_table = u'user_group_map'

#
# Extra information for users
#

class UserProfile(models.Model):
    user = models.ForeignKey('auth.User', unique=True, related_name='profile')
    phone_number = models.CharField(blank=True, default='', max_length=128)
    url = models.URLField(blank=True, default='')
    im = models.CharField(blank=True, default='', max_length=128)
    im_type_id = models.IntegerField(blank=True, default=1, max_length=4, null=True)
    address = models.TextField(blank=True, default='')
    notes = models.TextField(blank=True, default='')
    class Meta:
        db_table = u'tcms_user_profiles'

    def get_im(self):
        from forms import IM_CHOICES

        if not self.im:
            return None

        for c in IM_CHOICES:
            if self.im_type_id == c[0]:
                return '[%s] %s' % (c[1], self.im)

#
# TCMS Bookmarks in profile models
#

class BookmarkCategory(models.Model):
    user = models.ForeignKey('auth.User')
    name = models.CharField(max_length=1024)
    class Meta:
        db_table = u'tcms_bookmark_categories'

    def __unicode__(self):
        return self.name

class Bookmark(TCMSContentTypeBaseModel):
    user = models.ForeignKey('auth.User')
    category = models.ForeignKey(BookmarkCategory, blank=True, null=True, related_name='bookmark')
    name = models.CharField(max_length=1024)
    description = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=8192)
    class Meta:
        db_table = u'tcms_bookmarks'

    def __unicode__(self):
        return self.name
