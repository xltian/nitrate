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
from tcms.core.models import TCMSActionModel, BlobField
from tcms.core.utils.xmlrpc import XMLRPCSerializer
from tcms.core.utils import calc_percent

try:
    from tcms.core.contrib.plugins_support.signals import register_model
except ImportError:
    register_model = None

# Products zone

def get_as_choices(iterable, allow_blank):
    # Generate a list of (id, string) pairs suitable
    # for a ChoiceField's "choices".
    #
    # Prepend with a blank entry if "allow_blank" is True
    #
    # Turn each object in the list into a choice
    # using its "as_choice" method
    if allow_blank:
        result = [('', '')]
    else:
        result = []
    result += [obj.as_choice() for obj in iterable]
    return result

def get_all_choices(cls, allow_blank=True):
    # Generate a list of (id, string) pairs suitable
    # for a ChoiceField's "choices", based on all instances of a class:
    return get_as_choices(cls.objects.all(), allow_blank)

class Classification(TCMSActionModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=64)
    description = models.TextField(blank=True)
    sortkey = models.IntegerField(default=0)
    class Meta:
        db_table = u'classifications'
        ordering = ['sortkey', 'id']
    
    def __unicode__(self):
        return self.name

class Product(TCMSActionModel):
    id = models.AutoField(max_length=5, primary_key=True)
    name = models.CharField(unique=True, max_length=64)
    classification = models.ForeignKey(Classification)
    description = models.TextField(blank=True)
    milestone_url = models.CharField(
        db_column='milestoneurl', max_length=128, default='---'
    )
    disallow_new = models.BooleanField(db_column='disallownew')
    vote_super_user = models.IntegerField(
        db_column = 'votesperuser', null = True, default = 1,
    )
    max_vote_super_bug = models.IntegerField(
        db_column='maxvotesperbug', max_length=6, default=10000
    )
    votes_to_confirm = models.BooleanField(
        db_column='votestoconfirm', max_length=6
    )
    default_milestone = models.CharField(
        db_column='defaultmilestone', max_length=20, default='---'
    )
    
    class Meta:
        ordering = ['name']
        db_table = u'products'
        
    # Auto-generated attributes from back-references:
    #   'components' : QuerySet of Components (from Components.product)
    #   'versions' : QuerySet of Versions (from Versions.product)
    #   'builds' : QuerySet of TestBuilds (from TestBuilds.product)
    #   'environments' : QuerySet of TestEnvironments (from TestEnvironments.product)
    #   'environment_categories': QuerySet of TestEnvironmentCategory
    
    def __unicode__(self):
        return self.name
    
    def save(self):
        super(Product, self).save()
        self.category.get_or_create(name='--default--')
        self.version.get_or_create(value='unspecified')
        self.build.get_or_create(name='unspecified')
    
    def get_version_choices(self, allow_blank):
        # Generate a list of (id, string) pairs suitable
        # for a ChoiceField's "choices":
        return get_as_choices(self.version.all(), allow_blank)
    
    def get_build_choices(self, allow_blank, only_active):
        # Generate a list of (id, string) pairs suitable
        # for a ChoiceField's "choices"
        #
        # @only_active: restrict to only show builds flagged as "active"
        q = self.build
        if only_active:
            q = q.filter(is_active=True)
        return get_as_choices(q.all(), allow_blank)
    
    def get_environment_choices(self, allow_blank):
        # Generate a list of (id, string) pairs suitable
        # for a ChoiceField's "choices":
        return get_as_choices(self.environments.all(), allow_blank)
    
    @classmethod
    def get_choices(cls, allow_blank):
        # Generate a list of (id, string) pairs suitable
        # for a ChoiceField's "choices":
        print cls.objects.all()
        return get_as_choices(cls.objects.order_by('name').all(), allow_blank)
    
    def as_choice(self):
        return (self.id, self.name)
        
class Priority(TCMSActionModel):
    id = models.AutoField(max_length=5, primary_key=True)
    value = models.CharField(unique=True, max_length=64)
    sortkey = models.IntegerField(max_length=6, default=0)
    is_active = models.BooleanField(db_column='isactive', default=True)
        
    class Meta:
        db_table = u'priority'
        verbose_name_plural = u'priorities'
        ordering = ['value', ]
    
    def __unicode__(self):
        return self.value

class Milestone(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product)
    value = models.CharField(unique=True, max_length=60)
    sortkey = models.IntegerField(default=0)
    
    class Meta:
        db_table = u'milestones'
    
    def __unicode__(self):
        return unicode(self.value)

class Component(TCMSActionModel):
    id = models.AutoField(max_length=5, primary_key=True)
    name = models.CharField(max_length=64)
    product = models.ForeignKey(Product, related_name='component')
    initial_owner = models.ForeignKey(
        'auth.User',
        db_column='initialowner',
        related_name='initialowner',
        null=True
    )
    initial_qa_contact = models.ForeignKey(
        'auth.User',
        db_column='initialqacontact',
        related_name='initialqacontact',
        blank=True,
        null=True
    )
    description = models.TextField()
    
    # Auto-generated attributes from back-references:
    #   'cases' : list of TestCases (from TestCases.components)
    
    class Meta:
        db_table = u'components'
        unique_together = ('product', 'name')
        ordering = ['name', ]
    
    def __unicode__(self):
        return self.name

class Version(TCMSActionModel):
    id = models.AutoField(primary_key=True)
    value = models.CharField(max_length=192)
    product = models.ForeignKey(Product, related_name='version')
    
    class Meta:
        db_table = u'versions'
        unique_together = ('product', 'value')
        ordering = ['-value']
    
    def __unicode__(self):
        return self.value

    #update version when edit or create
    def save(self, *args, **kwargs):
        """Save version and update the relative test plans"""
        super(Version, self).save(*args, **kwargs) # Call the "real" save() method.
        test_plan_list = self.testplan_set.all()
        for tp in test_plan_list:
            tp.default_product_version = self.value
            tp.save()
    
    @classmethod
    def id_to_string(cls, id):
        # Utility function to help with test_plans.default_product_version
        # Convert a version ID to a string:
        try:
            version_string = cls.objects.get(id=id).value
        except cls.DoesNotExist:
            version_string = None
            
        return version_string
    
    @classmethod
    def string_to_id(cls, product_id, value):
        try:
            version_id = cls.objects.get(product__id=product_id, value=value).id
        except cls.DoesNotExist:
            version_id = None
            
        return version_id
    
    def as_choice(self):
        return (self.id, self.value)
    
#  Test builds zone
class TestBuildManager(models.Manager):
    
    pass
#    def get_plans_count(self):
#        return sum(self.values_list('plans_count', flat = True))

class TestBuild(TCMSActionModel):
    build_id = models.AutoField(max_length=10, unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    product = models.ForeignKey(Product, related_name='build')
    milestone = models.CharField(max_length=20,default='---')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(db_column='isactive', default=True)
    objects = TestBuildManager()
    
    class Meta:
        db_table = u'test_builds'
        unique_together = ('product', 'name')
        ordering = ['-name']
        verbose_name = u'build'
        verbose_name_plural = u'builds'
    
    @classmethod
    def list(cls, query):
        q = cls.objects
        
        if query.get('build_id'):
            q = q.filter(build_id = query['build_id'])
        if query.get('name'):
            q = q.filter(name = query['name'])
        if query.get('product'):
            q = q.filter(product = query['product'])
        if query.get('product_id'):
            q = q.filter(product__id = query['product_id'])
        if query.get('milestone'):
            q = q.filter(milestone = query['milestone'])
        if query.get('is_active'):
            q = q.filter(is_active = query['is_active'])
        
        return q.all()
    
    @classmethod
    def list_active(cls, query = {}):
        if isinstance(query, dict): query['is_active'] = True
        return cls.list(query)
    
    def __unicode__(self):
        return self.name
    
    def as_choice(self):
        return (self.build_id, self.name)

    def get_case_runs_failed_percent(self):
        if hasattr(self, 'case_runs_failed_count'):
            return calc_percent(self.case_runs_failed_count, self.case_runs_count)
        else:
            return None 
    
    def get_case_runs_passed_percent(self):
        if hasattr(self, 'case_runs_passed_count'):
            return calc_percent(self.case_runs_passed_count, self.case_runs_count)
        else:
            return None 

# Test environments zone

class TestEnvironment(TCMSActionModel):
    environment_id = models.AutoField(
        max_length=10,
        primary_key=True
    )
    product = models.ForeignKey(Product, related_name='environments')
    name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(db_column="isactive", default=True)
    
    class Meta:
        db_table = u'test_environments'
    
    def __unicode__(self):
        return self.name
    
    def as_choice(self):
        return (self.environment_id, self.name)

class TestEnvironmentCategory(models.Model):
    env_category_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='environment_categories')
    name = models.CharField(unique=True, max_length=255, blank=True)
    class Meta:
        db_table = u'test_environment_category'
    
    def __unicode__(self):
        return self.name

class TestEnvironmentElement(models.Model):
    element_id = models.AutoField(max_length=10, primary_key=True)
    env_category = models.ForeignKey(TestEnvironmentCategory)
    name = models.CharField(unique=True, max_length=255, blank=True)
    parent = models.ForeignKey('self', null=True, related_name='parent_set')
    is_private = models.IntegerField(db_column='isprivate', max_length=4)
    class Meta:
        db_table = u'test_environment_element'
    
    def __unicode__(self):
        return self.name

class TestEnvironmentProperty(models.Model):
    property_id = models.IntegerField(primary_key=True)
    element = models.ForeignKey(TestEnvironmentElement)
    name = models.CharField(unique=True, max_length=255, blank=True)
    valid_express = models.TextField(db_column='validexp', blank=True)
    class Meta:
        db_table = u'test_environment_property'
    
    def __unicode__(self):
        return self.name

class TestEnvironmentMap(models.Model):
    environment = models.ForeignKey(TestEnvironment, primary_key=True)
    property = models.ForeignKey(TestEnvironmentProperty)
    element = models.ForeignKey(TestEnvironmentElement)
    value_selected = models.TextField(blank=True)
    class Meta:
        db_table = u'test_environment_map'
    
    def __unicode__(self):
        return self.value_selected

# Test tag zone
class TestTag(TCMSActionModel):
    id = models.AutoField(db_column='tag_id', max_length=10, primary_key=True)
    name = models.CharField(db_column='tag_name', max_length=255)
    class Meta:
        db_table = u'test_tags'
        verbose_name = u'tag'
        verbose_name_plural = u'tags'
    
    def __unicode__(self):
        return self.name
    
    @classmethod
    def string_to_list(cls, string):
        from tcms.core.utils import string_to_list
        return string_to_list(string)

    @classmethod
    def get_or_create_many_by_name(cls, names):
        tags = []
        for name in names:
            new_tag = cls.objects.get_or_create(name=name)[0]
            tags.append(new_tag)
        return tags

# Test attachements file zone

class TestAttachment(models.Model):
    attachment_id = models.AutoField(max_length=10, primary_key=True)
    submitter = models.ForeignKey(
        'auth.User',
        related_name='attachments',
        blank=True,
        null=True
    )
    description = models.CharField(max_length=1024, blank=True)
    file_name = models.CharField(db_column='filename', max_length=255, unique=True, blank=True)
    stored_name = models.CharField(max_length=128, unique=True, blank=True, null=True)
    create_date = models.DateTimeField(db_column='creation_ts')
    mime_type = models.CharField(max_length=100)
    def __unicode__(self):
        return self.file_name
        
    class Meta:
        db_table = u'test_attachments'

class TestAttachmentData(models.Model):
    attachment = models.ForeignKey(TestAttachment, primary_key=True)
    contents = BlobField(blank=True)
    class Meta:
        db_table = u'test_attachment_data'

# ============================
# New TCMS Environments models
# ============================

class TCMSEnvGroup(TCMSActionModel):
    name = models.CharField(unique=True, max_length=255)
    manager = models.ForeignKey('auth.User', related_name='env_group_manager')
    modified_by = models.ForeignKey(
        'auth.User',
        related_name='env_group_modifier',
        blank=True,
        null=True
    )
    is_active = models.BooleanField(default=True)
    property = models.ManyToManyField(
        'management.TCMSEnvProperty',
        through='management.TCMSEnvGroupPropertyMap',
        related_name='group'
    )
    
    class Meta:
        db_table = u'tcms_env_groups'
        ordering = ['name']
    
    def __unicode__(self):
        return unicode(self.name)
    
    @classmethod
    def get_active(cls):
        return cls.objects.filter(is_active=True)

class TCMSEnvPlanMap(models.Model):
    plan = models.ForeignKey('testplans.TestPlan')
    group = models.ForeignKey(TCMSEnvGroup)
    
    class Meta:
        db_table = u'tcms_env_plan_map'

class TCMSEnvProperty(TCMSActionModel):
    name = models.CharField(unique=True, max_length=255)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = u'tcms_env_properties'
        ordering = ['name']
    
    def __unicode__(self):
        return unicode(self.name)
    
    @classmethod
    def get_active(cls):
        return cls.objects.filter(is_active=True)

class TCMSEnvGroupPropertyMap(models.Model):
    group = models.ForeignKey(TCMSEnvGroup)
    property = models.ForeignKey(TCMSEnvProperty)
    
    class Meta:
        db_table = u'tcms_env_group_property_map'

class TCMSEnvValue(TCMSActionModel):
    value = models.CharField(max_length=255)
    property = models.ForeignKey(TCMSEnvProperty, related_name='value')
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = u'tcms_env_values'
        ordering = ['value']
        unique_together = ('property', 'value')
    
    def __unicode__(self):
        return unicode(self.value)
    
    @classmethod
    def get_active(cls):
        return cls.objects.filter(is_active=True)

if register_model:
    register_model(Classification)
    register_model(Product)
    register_model(Priority)
    register_model(Version)
    register_model(TestBuild)
    register_model(TestTag)
    register_model(Component)
    register_model(TCMSEnvGroup)
    register_model(TCMSEnvValue)
    register_model(TestAttachment)
