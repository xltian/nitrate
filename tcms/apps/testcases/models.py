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
#   Xuqing Kuang <xkuang@redhat.com>, Chenxiong Qi <cqi@redhat.com>

# from stdlib
from datetime import datetime
from itertools import ifilter

# from django
from django.core.urlresolvers import reverse
from django.core.exceptions import MultipleObjectsReturned
from django.conf import settings
from django.db import models, connection, transaction
from django.db.models import ObjectDoesNotExist
from django.db.models.signals import post_save, post_delete
from django.contrib.contenttypes import generic

# from tcms
from tcms.core.models import TCMSActionModel, TimedeltaField
from tcms.core.models import TCMSContentTypeBaseModel

#from signal listen
from tcms.apps.testcases import signals as case_watchers

try:
    from tcms.core.contrib.plugins_support.signals import register_model
except ImportError:
    register_model = None

AUTOMATED_CHOICES = (
    (0, 'Manual'),
    (1, 'Auto'),
    (2, 'Both'),
)

class NoneText:
    author = None
    case_text_version = 0
    action = None
    effect = None
    setup = None
    breakdown = None
    create_date = datetime.now()

class TestCaseStatus(TCMSActionModel):
    id = models.AutoField(
        db_column='case_status_id', max_length=6, primary_key=True
    )
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = u'test_case_status'
        verbose_name = "Test case status"
        verbose_name_plural = "Test case status"

    def __unicode__(self):
        return self.name

    @classmethod
    def get_PROPOSED(cls):
        try:
            return cls.objects.get(name='PROPOSED')
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_CONFIRMED(cls):
        try:
            return cls.objects.get(name='CONFIRMED')
        except cls.DoesNotExist:
            return None

    @classmethod
    def string_to_instance(self, name):
        return cls.objects.get(name=name)

    @classmethod
    def id_to_string(cls, id):
        try:
            return cls.objects.get(id = id).name
        except cls.DoesNotExist:
            return None

    def is_confirmed(self):
        return self.name == 'CONFIRMED'

class TestCaseCategory(TCMSActionModel):
    id = models.AutoField(db_column='category_id', primary_key=True)
    name = models.CharField(max_length=720)
    product = models.ForeignKey('management.Product', related_name="category")
    description = models.TextField(blank=True)

    class Meta:
        db_table = u'test_case_categories'
        verbose_name_plural = u'test case categories'
        unique_together = ('product', 'name')

    def __unicode__(self):
        return self.name

class TestCase(TCMSActionModel):
    case_id = models.AutoField(max_length=10, primary_key=True)
    create_date = models.DateTimeField(
        db_column='creation_date', auto_now_add=True
    )
    is_automated = models.IntegerField(
        db_column='isautomated', default = 0, max_length=4,
    )
    is_automated_proposed = models.BooleanField(default = False)
    script = models.TextField(blank=True)
    arguments = models.TextField(blank=True)
    extra_link = models.CharField(
        max_length=1024,
        default=None,
        blank=True,
        null=True
    )
    summary = models.CharField(max_length=255, blank=True)
    requirement = models.CharField(max_length=255, blank=True)
    alias = models.CharField(max_length=255, blank=True)
    estimated_time = TimedeltaField(null=True, blank=True)
    notes = models.TextField(blank=True)
    case_status = models.ForeignKey(TestCaseStatus)
    category = models.ForeignKey(
        TestCaseCategory, related_name='category_case'
    )
    priority = models.ForeignKey(
        'management.Priority', related_name='priority_case'
    )
    author = models.ForeignKey(
        'auth.User', related_name='cases_as_author'
    )
    default_tester = models.ForeignKey(
        'auth.User', related_name='cases_as_default_tester', blank = True, null=True
    )
    reviewer = models.ForeignKey(
        'auth.User', related_name='cases_as_reviewer', null=True
    )
    attachment = models.ManyToManyField(
        'management.TestAttachment',
        through='testcases.TestCaseAttachment',
    )

    plan = models.ManyToManyField(
        'testplans.TestPlan',
        through='testcases.TestCasePlan',
    )

    component = models.ManyToManyField(
        'management.Component',
        through='testcases.TestCaseComponent',
    )

    tag = models.ManyToManyField(
        'management.TestTag',
        through='testcases.TestCaseTag',
    )

    # Auto-generated attributes from back-references:
    #   'texts' : list of TestCaseTexts (from TestCaseTexts.case)
    class Meta:
        db_table = u'test_cases'
        ordering = ['summary', 'case_id',]

    def __unicode__(self):
        return self.summary

    @classmethod
    def create(cls, author, values):
        """
        Create the case element based on models/forms.
        """
        case = cls.objects.create(
            author = author,
            is_automated = values['is_automated'],
            is_automated_proposed = values['is_automated_proposed'],
            # sortkey = values['sortkey'],
            script = values['script'],
            arguments = values['arguments'],
            extra_link = values['extra_link'],
            summary = values['summary'],
            requirement = values['requirement'],
            alias = values['alias'],
            estimated_time = values['estimated_time'],
            case_status = values['case_status'],
            category = values['category'],
            priority = values['priority'],
            default_tester = values['default_tester'],
            notes = values['notes'],
        )
        tags = values.get('tag')
        if tags:
            map(lambda c: case.add_tag(c), tags)
        return case

    @classmethod
    def update(cls, case_ids, values):
        if isinstance(case_ids, int):
            case_ids = [case_ids, ]

        fields = [field.name for field in cls._meta.fields]

        tcs = cls.objects.filter(pk__in = case_ids)

        for k, v in values.items():
            if k in fields and v is not None and v != u'':
                tcs.update(**{k: v})

        return tcs

    @classmethod
    def list(cls, query, plan=None):
        """List the cases with request"""
        from django.db.models import Q
        if not plan:
            q = cls.objects
        else:
            q = cls.objects.filter(plan=plan)
        if query.get('search'):
            q = q.filter(
                Q(pk__icontains = query['search'])
                | Q(summary__icontains = query['search'])
                | Q(author__email__startswith = query['search'])
            )

        if query.get('summary'):
            q = q.filter(Q(summary__icontains=query['summary']))

        if query.get('author'):
            q = q.filter(
                Q(author__first_name__startswith = query['author'])
                | Q(author__last_name__startswith = query['author'])
                | Q(author__username__icontains = query['author'])
                | Q(author__email__startswith = query['author'])
            )

        if query.get('default_tester'):
            q = q.filter(
                Q(default_tester__first_name__startswith = query['default_tester'])
                | Q(default_tester__last_name__startswith = query['default_tester'])
                | Q(default_tester__username__icontains = query['default_tester'])
                | Q(default_tester__email__startswith = query['default_tester'])
            )

        if query.get('tag__name__in'):
            q = q.filter(tag__name__in = query['tag__name__in'])

        if query.get('category'):

            q = q.filter(category__name = query['category'].name)

        if query.get('priority'):
            q = q.filter(priority__in = query['priority'])

        if query.get('case_status'):
            q = q.filter(case_status__in = query['case_status'])

        #If plan exists, remove leading and trailing whitespace from it.
        plan_str = query.get('plan','').strip()
        if plan_str:
            try:
                # Is it an integer?  If so treat as a plan_id:
                plan_id = int(plan_str)
                q = q.filter(plan__plan_id = plan_id)
            except ValueError:
                # Not an integer - treat plan_str as a plan name:
                q = q.filter(plan__name__icontains = plan_str)
        del plan_str

        if query.get('product'):
            q = q.filter(category__product=query['product'])

        if query.get('component'):
            q = q.filter(component = query['component'])

        if query.get('bug_id'):
            q = q.filter(case_bug__bug_id__in = query['bug_id'])

        if query.get('is_automated'):
            q = q.filter(is_automated = query['is_automated'])

        if query.get('is_automated_proposed'):
            q = q.filter(is_automated_proposed = query['is_automated_proposed'])

        return q.distinct()

    @classmethod
    def list_confirmed(self):
        confirmed_case_status = TestCaseStatus.get_CONFIRMED()

        query = {
            'case_status_id': confirmed_case_status.case_status_id,
        }

        return cls.list(query)

    @classmethod
    def mail_scene(cls, objects, field = None, value = None, ctype = None, object_pk = None):
        tcs = objects.select_related()
        scence_templates = {
            'reviewer': {
                'template_name': 'mail/change_case_reviewer.txt',
                'subject': 'You have been speicific to be the reviewer of cases',
                'to_mail': list(set(tcs.values_list('reviewer__email', flat=True))),
                'context': {'test_cases': tcs},
            }
        }

        return scence_templates.get(field)

    def add_bug(self, bug_id, bug_system, summary = None, description = None, case_run = None):
        try:
            self.case_bug.get_or_create(
                bug_id = bug_id,
                case_run = case_run,
                bug_system = bug_system,
                summary = summary,
                description = description,
            )
        except:
            raise

    def add_component(self, component):
        try:
            return TestCaseComponent.objects.create(
                case = self,
                component = component,
            )
        except:
            raise

    def add_tag(self, tag):
        try:
            return TestCaseTag.objects.get_or_create(
                case = self,
                tag = tag
            )
        except:
            raise

    def update_tags(self, new_tags):
        '''
        Update case.tag
        so that case.tag == new_tags
        '''
        if not new_tags: return
        owning_tags = set(self.tag.all())
        new_tags = set(new_tags)
        tags_to_remove = owning_tags.difference(new_tags)
        tags_to_add = new_tags.difference(owning_tags)
        map(lambda c: self.add_tag(c), tags_to_add)
        map(lambda c: self.remove_tag(c), tags_to_remove)

    def add_text(
        self,
        action,
        effect,
        setup,
        breakdown,
        author = None,
        create_date = datetime.now(),
        case_text_version = 1,
    ):
        if not author:
            author = self.author

        latest_text = self.latest_text()
        if latest_text.action != action or latest_text.effect != effect \
        or latest_text.setup != setup or latest_text.breakdown != breakdown:
            case_text_version = latest_text.case_text_version + 1

            try:
                latest_text = TestCaseText.objects.create(
                    case = self,
                    case_text_version = case_text_version,
                    create_date = create_date,
                    author = author,
                    action = action,
                    effect = effect,
                    setup = setup,
                    breakdown = breakdown,
                )
            except:
                raise

        return latest_text

    def add_to_plan(self, plan):

        try:
            TestCasePlan.objects.get(case = self, plan = plan)
        except TestCasePlan.DoesNotExist:
            TestCasePlan.objects.get_or_create(
                case = self,
                plan = plan,
            )

    def clear_components(self):
        try:
            return TestCaseComponent.objects.filter(
                case = self,
            ).delete()
        except:
            raise

    def get_bugs(self):
        return TestCaseBug.objects.select_related(
            'case_run', 'bug_system__url_reg_exp'
        ).filter(case__case_id = self.case_id)

    def get_components(self):
        return self.component.all()

    def get_component_names(self):
        return self.component.values_list('name', flat=True)

    def get_choiced(self, obj_value, choices):
        for x in choices:
            if x[0] == obj_value:
                return x[1]

    def get_is_automated(self):
        return self.get_choiced(self.is_automated, AUTOMATED_CHOICES)

    def get_is_automated_form_value(self):
        if self.is_automated == 2:
            return [0, 1]

        return (self.is_automated, )

    def get_is_automated_status(self):
        return self.get_is_automated() + (self.is_automated_proposed and ' (Autoproposed)' or '')

    def get_previous_and_next(self, pk_list):
        pk_list = list(pk_list)
        current_idx = pk_list.index(self.pk)
        prev = TestCase.objects.get(pk = pk_list[current_idx - 1])
        try:
            next = TestCase.objects.get(pk = pk_list[current_idx + 1])
        except IndexError:
            next = TestCase.objects.get(pk = pk_list[0])

        return (prev, next)

    def get_text_with_version(self, case_text_version = None):
        if case_text_version:
            try:
                return TestCaseText.objects.get(
                    case__case_id = self.case_id,
                    case_text_version = case_text_version
                )
            except TestCaseText.DoesNotExist, error:
                return NoneText

        return self.latest_text()

    def latest_text(self):
        try:
            return self.text.order_by('-case_text_version')[0]
        except IndexError:
            return NoneText

    def mail(self, template, subject, context = {}, to = [], request = None):
        from tcms.core.utils.mailto import mailto
        if not to:
            to = self.author.email

        to = list(set(to))
        mailto(template, subject, to, context, request)

    def remove_bug(self, bug_id, run_id=None):
        bugs = self.case_bug.filter(bug_id=bug_id)
        if run_id:
            bugs = bugs.filter(case_run=run_id)
        bugs.delete()

    def remove_component(self, component):
        cursor = connection.cursor()
        cursor.execute("DELETE from test_case_components \
            WHERE case_id = %s AND component_id = %s",
            (self.case_id, component.id)
        )

    def remove_plan(self, plan):
        cursor = connection.cursor()
        cursor.execute("DELETE from test_case_plans \
            WHERE plan_id = %s \
            AND case_id = %s",
            (plan.plan_id, self.case_id)
        )

    def remove_tag(self, tag):
        cursor = connection.cursor()
        cursor.execute("DELETE from test_case_tags \
            WHERE case_id = %s \
            AND tag_id = %s",
            (self.pk, tag.pk)
        )

    def get_url_path(self, request = None):
        return reverse('tcms.apps.testcases.views.get', args=[self.pk, ])

    def _get_email_conf(self):
        try:
            return self.email_settings
        except ObjectDoesNotExist:
            return TestCaseEmailSettings.objects.create(case=self)
    emailing = property(_get_email_conf)

class TestCaseText(TCMSActionModel):

    case = models.ForeignKey(TestCase, related_name='text')
    case_text_version = models.IntegerField(max_length=9)
    author = models.ForeignKey('auth.User', db_column='who')
    create_date = models.DateTimeField(db_column='creation_ts', auto_now_add=True)
    action = models.TextField(blank=True)
    effect = models.TextField(blank=True)
    setup = models.TextField(blank=True)
    breakdown = models.TextField(blank=True)

    class Meta:
        db_table = u'test_case_texts'
        ordering = ['case', '-case_text_version']
        unique_together = ('case', 'case_text_version')

    def get_plain_text(self):
        from tcms.core.utils.html import html2text
        from django.utils.encoding import smart_str

        self.action = html2text(smart_str(self.action))
        self.effect = html2text(smart_str(self.effect))
        self.setup = html2text(smart_str(self.setup))
        self.breakdown = html2text(smart_str(self.breakdown))

        return self

class TestCasePlan(models.Model):
    # plan_id = models.IntegerField(max_length=11, primary_key=True)
    # case_id = models.IntegerField(max_length=11, primary_key=True)

    plan = models.ForeignKey('testplans.TestPlan')
    case = models.ForeignKey(TestCase)
    sortkey = models.IntegerField(max_length=11, null=True, blank=True)

    class Meta:
        db_table = u'test_case_plans'


class TestCaseAttachment(models.Model):
    attachment = models.ForeignKey(
        'management.TestAttachment', primary_key=True
    )
    case = models.ForeignKey(
        TestCase, default=None, related_name='case_attachment'
    )
    case_run = models.ForeignKey(
        'testruns.TestCaseRun',
        default=None,
        related_name='case_run_attachment'
    )
    class Meta:
        db_table = u'test_case_attachments'

class TestCaseComponent(models.Model):
    case = models.ForeignKey(TestCase, primary_key=True) # case_id
    component = models.ForeignKey('management.Component') # component_id
    class Meta:
        db_table = u'test_case_components'

    #def __unicode__(self):
        #Another choice: return the related case summary too?
    #    return "%s, %s" %(self.component.name, self.case.summary)

class TestCaseTag(models.Model):
    tag = models.ForeignKey(
        'management.TestTag'
    )
    case = models.ForeignKey(TestCase)
    user = models.IntegerField(db_column='userid', default='0')

    class Meta:
        db_table = u'test_case_tags'

class TestCaseBugSystem(TCMSActionModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    url_reg_exp = models.CharField(max_length=8192)

    class Meta:
        db_table = u'test_case_bug_systems'

    def __unicode__(self):
        return self.name

class TestCaseBug(TCMSActionModel):
    bug_id = models.IntegerField()
    case_run = models.ForeignKey(
        'testruns.TestCaseRun',
        related_name='case_run_bug',
        default=None, blank=True, null=True
    )
    case = models.ForeignKey(
        TestCase,
        related_name='case_bug',
    )
    bug_system = models.ForeignKey(TestCaseBugSystem, default=1)
    summary = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = u'test_case_bugs'
        unique_together = (
            ('bug_id', 'case_run', 'case'),
            ('bug_id', 'case_run')
        )

    def __unicode__(self):
        return str(self.bug_id)

    def get_name(self):
        if self.summary:
            return self.summary

        return self.bug_id

    def get_absolute_url(self):
        # Upward compatibility code
        return self.get_url()

    def get_url(self):
        return self.bug_system.url_reg_exp % self.bug_id

class Contact(TCMSContentTypeBaseModel):
    ''' A Contact that can be added into Email settings' CC list '''

    name = models.CharField(max_length=50)
    email = models.EmailField(db_index=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'tcms_contacts'

    @classmethod
    def create(cls, email, content_object, name=None):
        ''' Factory method to create a new Contact '''

        if not name:
            store_name = email.split('@')[0]
        else:
            store_name = name

        c = cls(name=store_name,
                email=email,
                content_object=content_object,
                site_id=settings.SITE_ID)
        c.save()
        return c

class TestCaseEmailSettings(models.Model):
    case = models.OneToOneField(TestCase, related_name='email_settings')
    notify_on_case_update = models.BooleanField(default=False)
    notify_on_case_delete = models.BooleanField(default=False)
    auto_to_case_author = models.BooleanField(default=False)
    auto_to_case_tester = models.BooleanField(default=False)
    auto_to_run_manager = models.BooleanField(default=False)
    auto_to_run_tester  = models.BooleanField(default=False)
    auto_to_case_run_assignee = models.BooleanField(default=False)

    cc_list = generic.GenericRelation(Contact, object_id_field='object_pk')

    class Meta:
        pass

    def add_cc(self, email_addrs):
        '''Add email addresses to CC list

        Arguments:
        - email_addrs: str or list, holding one or more email addresses
        '''

        emailaddr_list = []
        if not isinstance(email_addrs, list):
            emailaddr_list.append(email_addr)
        else:
            emailaddr_list = list(email_addrs)

        for email_addr in emailaddr_list:
            Contact.create(email=email_addr, content_object=self)

    def get_cc_list(self):
        ''' Return the whole CC list '''

        return [c.email for c in self.cc_list.all()]

    def remove_cc(self, email_addrs):
        '''Remove one or more email addresses from EmailSettings' CC list

        If any email_addr is unknown, remove_cc will keep quiet.

        Arguments:
        - email_addrs: str or list, holding one or more email addresses
        '''

        emailaddr_list = []
        if not isinstance(email_addrs, list):
            emailaddr_list.append(email_addrs)
        else:
            emailaddr_list = list(email_addrs)

        self.cc_list.filter(email__in=emailaddr_list).delete()

    def filter_new_emails(self, origin_emails, new_emails):
        ''' Find out the new email addresses to be added '''

        return list(set(new_emails) - set(origin_emails))

    def filter_unnecessary_emails(self, origin_emails, new_emails):
        ''' Find out the unnecessary addresses to be delete '''

        return list(set(origin_emails) - set(new_emails))

    def update_cc_list(self, email_addrs):
        '''Add the new emails and delete unnecessary ones

        Arguments:
        - email_addrs: list, a instance of list holding emails user input via UI
        '''

        origin_emails = self.get_cc_list()

        emails_to_delete = self.filter_unnecessary_emails(origin_emails, email_addrs)
        self.remove_cc(emails_to_delete)
        self.add_cc(self.filter_new_emails(origin_emails, email_addrs))

def _listen():
    """ signals listen """

    # case save/delete listen for email notify
    post_save.connect(case_watchers.on_case_save, TestCase)
    post_delete.connect(case_watchers.on_case_delete, TestCase)

if settings.LISTENING_MODEL_SIGNAL:
    _listen()

if register_model:
    register_model(TestCase)
    register_model(TestCaseText)
    register_model(TestCasePlan)
    register_model(TestCaseBug)
    register_model(TestCaseComponent)
