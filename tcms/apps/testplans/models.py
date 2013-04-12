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

from datetime import datetime

from django.core.urlresolvers import reverse
from django.db import models, connection, transaction
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.utils.safestring import mark_safe, SafeData
from django.db.models.signals import post_save, post_delete
from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify

from tcms.core.models import TCMSActionModel

from tcms.apps.management.models import TCMSEnvPlanMap, Version
from tcms.apps.testcases.models import TestCasePlan

# single listen
from tcms.apps.testplans import signals as plan_watchers

try:
    from tcms.core.contrib.plugins_support.signals import register_model
except ImportError:
    register_model = None

class TestPlanType(TCMSActionModel):
    id = models.AutoField(db_column='type_id', primary_key=True)
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True, null=True)
    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'test_plan_types'
        ordering = ['name']

class TestPlan(TCMSActionModel):
    """
    A plan within the TCMS
    """
    plan_id = models.AutoField(max_length=11, primary_key=True)
    default_product_version = models.TextField()
    product_version = models.ForeignKey(Version, blank=True, null=True)
    name = models.CharField(max_length=255)
    create_date = models.DateTimeField(db_column='creation_date', auto_now_add=True)
    is_active = models.BooleanField(db_column='isactive', default=True)
    extra_link = models.CharField(
        max_length=1024,
        default=None,
        blank=True,
        null=True
    )

    owner  = models.ForeignKey('auth.User', blank=True, null=True, related_name='myplans')
    parent = models.ForeignKey('self', blank=True, null=True, related_name='child_set')
    author = models.ForeignKey('auth.User')
    product = models.ForeignKey('management.Product', related_name='plan')
    type = models.ForeignKey(TestPlanType)

    attachment = models.ManyToManyField(
        'management.TestAttachment',
        through='testplans.TestPlanAttachment',
    )

    case = models.ManyToManyField(
        'testcases.TestCase',
        through='testcases.TestCasePlan',
    )

    component = models.ManyToManyField(
        'management.Component', through='testplans.TestPlanComponent',
    )

    env_group = models.ManyToManyField(
        'management.TCMSEnvGroup',
        through='management.TCMSEnvPlanMap',
    )

    tag = models.ManyToManyField(
        'management.TestTag',
        through='testplans.TestPlanTag',
    )


    class Meta:
        db_table = u'test_plans'
        ordering = ['-plan_id', 'name']

    def __unicode__(self):
        return self.name

    #update version when edit or create
    def save(self, *args, **kwargs):
        """Save testplan and relate the default_product_version with Verion object.
        """
        new_version, is_created = Version.objects.get_or_create(
            product = self.product,
            value = self.default_product_version
        )
        self.product_version = new_version
        super(TestPlan, self).save(*args, **kwargs) # Call the "real" save() method.

    @classmethod
    def list(cls, query = None):
        """docstring for list_plans"""
        from django.db.models import Q

        new_query = {}

        for k, v in query.items():
            if v and k not in ['action', 't', 'f', 'a']:
                new_query[k] = hasattr(v, 'strip') and v.strip() or v

        # build a QuerySet:
        q = cls.objects
        # add any necessary filters to the query:

        if new_query.get('search'):
            q = q.filter(Q(plan_id__icontains = new_query['search']) \
                            | Q(name__icontains = new_query['search']))
            del new_query['search']

        return q.filter(**new_query).distinct()

    def confirmed_case(self):
        return self.case.filter(case_status__name = 'CONFIRMED')

    def latest_text(self):
        try:
            return self.text.select_related('author').order_by('-plan_text_version')[0]
        except IndexError:
            return None
        except ObjectDoesNotExist:
            return None

    def get_text_with_version(self, plan_text_version = None):
        if plan_text_version:
            try:
                return self.text.get(
                    plan_text_version = plan_text_version
                )
            except TestPlanText.DoesNotExist, error:
                return None

        return self.latest_text()

    def add_text(self,
        author,
        plan_text,
        create_date = datetime.now(),
        plan_text_version = None
    ):
        if not plan_text_version:
            latest_text = self.latest_text()
            if latest_text:
                plan_text_version = latest_text.plan_text_version + 1
            else:
                plan_text_version = 1

        try:
            return self.text.create(
                plan_text_version = plan_text_version,
                author = author,
                create_date = create_date,
                plan_text = plan_text
            )
        except:
            raise

    def add_case(self, case, sortkey=0):

        tcp, is_created = TestCasePlan.objects.get_or_create(
            plan = self,
            case = case,
        )
        if is_created:
            tcp.sortkey = sortkey
            tcp.save()

    def add_component(self, component):
        try:
            return TestPlanComponent.objects.create(
                plan = self,
                component = component,
            )
        except:
            return False

    def add_env_group(self, env_group):
        # Create the env plan map
        try:
            return TCMSEnvPlanMap.objects.create(
                plan = self,
                group = env_group,
            )
        except:
            raise

    def add_attachment(self, attachment):
        try:
            return TestPlanAttachment.objects.create(
                plan = self,
                attachment = attachment,
            )
        except:
            raise

    def add_tag(self, tag):
        try:
            return TestPlanTag.objects.get_or_create(
                plan = self,
                tag = tag
            )
        except:
            raise

    def remove_tag(self, tag):
        cursor = connection.cursor()
        cursor.execute("DELETE from test_plan_tags \
            WHERE plan_id = %s \
            AND tag_id = %s",
            (self.pk, tag.pk)
        )

    def remove_component(self, component):
        try:
            return TestPlanComponent.objects.get(
                plan = self, component = component
            ).delete()
        except:
            return False

    def clear_env_groups(self):
        # Remove old env groups because we only maintanence on group per plan.
        try:
            return TCMSEnvPlanMap.objects.filter(plan = self).delete()
        except:
            raise

    def delete_case(self, case):
        cursor = connection.cursor()
        cursor.execute("DELETE from test_case_plans \
            WHERE plan_id = %s \
            AND case_id = %s",
            (self.plan_id, case.case_id)
        )

    @models.permalink
    def get_absolute_url(self):
        return ('test_plan_url', (), {
            'plan_id': self.plan_id,
            'slug': slugify(self.name),
        })

    def get_url_path(self, request = None):
        return self.get_absolute_url()

    def get_default_product_version(self):
        """
        Workaround the schema problem with default_product_version
        Get a 'Versions' object based on a string query
        """
        return self.product_version

    def get_version_id(self):
        """
        Workaround the schema problem with default_product_version
        """
        version = self.get_default_product_version()
        return version and version.id or None

    def get_case_sortkey(self):
        """
        Get case sortkey.
        """
        if self.case.exists():
            max_sk = max(TestCasePlan.objects.filter(plan = self,
                case__in = self.case.all()).values_list('sortkey',
                flat = True))
            if max_sk:
                return max_sk + 10
            else:
                return None
        else:
            return None

    def _get_email_conf(self):
        try:
            return self.email_settings
        except ObjectDoesNotExist:
            return TestPlanEmailSettings.objects.create(plan=self)
    emailing = property(_get_email_conf)

class TestPlanText(TCMSActionModel):

    plan = models.ForeignKey(TestPlan, related_name='text')
    plan_text_version = models.IntegerField(max_length=11)
    author = models.ForeignKey('auth.User', db_column='who')
    create_date = models.DateTimeField(auto_now_add=True, db_column='creation_ts')
    plan_text = models.TextField(blank=True)

    class Meta:
        db_table = u'test_plan_texts'
        ordering = ['plan', '-plan_text_version']
        unique_together = ('plan', 'plan_text_version')

    def get_plain_text(self):
        from tcms.core.utils.html import html2text
        self.plan_text = html2text(self.plan_text)
        return self

class TestPlanPermission(models.Model):
    userid = models.IntegerField(max_length=9, unique=True, primary_key=True)
    permissions = models.IntegerField(max_length=4)
    grant_type = models.IntegerField(max_length=4, unique=True)

    plan = models.ForeignKey(TestPlan)

    class Meta:
        db_table = u'test_plan_permissions'
        unique_together = ('plan', 'userid')

class TestPlanPermissionsRegexp(models.Model):
    plan = models.ForeignKey(TestPlan, primary_key=True)
    user_regexp = models.TextField()
    permissions = models.IntegerField(max_length=4)
    class Meta:
        db_table = u'test_plan_permissions_regexp'

class TestPlanAttachment(models.Model):
    attachment = models.ForeignKey(
        'management.TestAttachment',
        primary_key=True
    )
    plan = models.ForeignKey(TestPlan)
    class Meta:
        db_table = u'test_plan_attachments'

class TestPlanActivity(models.Model):
    plan = models.ForeignKey(TestPlan) # plan_id
    fieldid = models.IntegerField()
    who = models.ForeignKey('auth.User', db_column='who')
    changed = models.DateTimeField(primary_key=True)
    oldvalue = models.TextField(blank=True)
    newvalue = models.TextField(blank=True)
    class Meta:
        db_table = u'test_plan_activity'

class TestPlanTag(models.Model):
    tag = models.ForeignKey(
        'management.TestTag'
    )
    plan = models.ForeignKey(TestPlan)
    user = models.IntegerField(default="1", db_column='userid')

    class Meta:
        db_table = u'test_plan_tags'

class TestPlanComponent(models.Model):
    plan = models.ForeignKey(TestPlan)
    component = models.ForeignKey('management.Component')

    class Meta:
        db_table = u'test_plan_components'
        unique_together = ('plan', 'component')

class TestPlanEmailSettings(models.Model):
    plan = models.OneToOneField(TestPlan, related_name='email_settings')
    is_active = models.BooleanField(default=False)
    auto_to_plan_owner = models.BooleanField(default=False)
    auto_to_plan_author = models.BooleanField(default=False)
    auto_to_case_owner = models.BooleanField(default=False)
    auto_to_case_default_tester = models.BooleanField(default=False)
    notify_on_plan_update = models.BooleanField(default=False)
    notify_on_plan_delete = models.BooleanField(default=False)
    notify_on_case_update = models.BooleanField(default=False)

    class Meta:
        pass

if register_model:
    register_model(TestPlan)
    register_model(TestPlanText)
    register_model(TestPlanType)
    register_model(TestPlanTag)
    register_model(TestPlanComponent)

def _listen():
    post_save.connect(plan_watchers.on_plan_save, TestPlan)
    post_delete.connect(plan_watchers.on_plan_delete, TestPlan)

if settings.LISTENING_MODEL_SIGNAL:
    _listen()
