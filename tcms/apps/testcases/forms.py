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

from datetime import timedelta

from django import forms

from tcms.core.forms import UserField, TimedeltaFormField, MultipleEmailField, TinyMCEWidget
from tcms.core.forms.widgets import SECONDS_PER_MIN, SECONDS_PER_HOUR

from tcms.apps.testplans.models import TestPlan
from tcms.apps.testruns.models import TestCaseRun
from tcms.apps.management.models import Priority, Product, Component, Version, TestTag

from models import TestCase, TestCaseCategory, TestCaseStatus
from models import TestCaseBug, AUTOMATED_CHOICES as FULL_AUTOMATED_CHOICES

from fields import MultipleEmailField

AUTOMATED_CHOICES = (
    (0, 'Manual'),
    (1, 'Auto'),
)

AUTOMATED_SERCH_CHOICES = (
    ('', '----------'),
    (0, 'Manual'),
    (1, 'Auto'),
    (2, 'Both'),
)

class BugField(forms.CharField):
    """
    Customizing forms CharFiled validation.
    Bug ID seperated using a delimiter such as comma.
    """
    def validate(self, value):
        from tcms.core.utils import string_to_list
        super(BugField, self).validate(value)
        error = 'Enter a valid Bug ID.'
        bug_ids = string_to_list(value)

        for bug_id in bug_ids:
            try:
                bug_id = int(bug_id)
            except ValueError, error:
                raise forms.ValidationError(error)
            if abs(bug_id) > 8388607:
                raise forms.ValidationError(error)



# =========== New Case ModelForm ==============
# The form works fine for web but broken for XML-RPC.
# So it's not in using yet.

class CaseModelForm(forms.ModelForm):
    default_tester = UserField(required = False)

    is_automated = forms.MultipleChoiceField(
        choices = AUTOMATED_CHOICES,
        widget = forms.CheckboxSelectMultiple(),
    )
    is_automated_proposed = forms.BooleanField(
        label = 'Autoproposed', widget = forms.CheckboxInput(),
        required = False
    )

    product = forms.ModelChoiceField(
        label = "Product",
        queryset = Product.objects.all(),
        empty_label = None,
    )
    category = forms.ModelChoiceField(
        label = "Category",
        queryset = TestCaseCategory.objects.none(),
        empty_label = None,
    )
    component = forms.ModelMultipleChoiceField(
        label = "Components",
        queryset = Component.objects.none(),
        required = False,
    )

    case_status = forms.ModelChoiceField(
        label = "Case status",
        queryset = TestCaseStatus.objects.all(),
        empty_label = None,
    )

    priority = forms.ModelChoiceField(
        label = "Priority",
        queryset = Priority.objects.all(),
        empty_label = None,
    )

    class Meta:
        model = TestCase
        exclude = ('author', )
        widgets = {
            'default_tester': UserField(),
        }

    #def clean_alias(self):
    #    data = self.cleaned_data['alias']
    #    tc_count = TestCase.objects.filter(alias = data).count()
    #
    #    if tc_count == 0:
    #        return data
    #    raise forms.ValidationError('Duplicated alias exist in database.')

    def clean_is_automated(self):
        data = self.cleaned_data['is_automated']
        if len(data) == 2:
            return 2

        if len(data):
            return data[0]

        return data

    def populate(self, product_id = None):
        # We can dynamically set choices for a form field:
        # Seen at: http://my.opera.com/jacob7908/blog/2009/06/19/django-choicefield-queryset (Chinese)
        # Is this documented elsewhere?
        if hasattr(self, 'product') and self.product and not product_id:
            product = self.product

        if product_id:
            self.fields['category'].queryset = TestCaseCategory.objects.filter(product__id = product_id)
            self.fields['component'].queryset = Component.objects.filter(product__id = product_id)
        else:
            self.fields['category'].queryset = TestCaseCategory.objects.all()
            self.fields['component'].queryset = Component.objects.all()

# =========== Forms for create/update ==============

class BaseCaseForm(forms.Form):
    summary = forms.CharField(label = "Summary",)
    default_tester = UserField(label = "Default tester", required = False)
    requirement = forms.CharField(label = "Requirement", required = False)
    is_automated = forms.MultipleChoiceField(
        choices = AUTOMATED_CHOICES,
        widget = forms.CheckboxSelectMultiple(),
    )
    is_automated_proposed = forms.BooleanField(
        label = 'Autoproposed', required = False
    )
    script = forms.CharField(label = "Script", required = False)
    arguments = forms.CharField(label = "Arguments", required = False)
    alias = forms.CharField(label = "Alias", required = False)
    extra_link = forms.URLField(
        label = 'Extra link',
        max_length = 1024,
        verify_exists = False,
        required = False
    )
    # sortkey = forms.IntegerField(label = 'Sortkey', required = False)
    case_status = forms.ModelChoiceField(
        label = "Case status",
        queryset = TestCaseStatus.objects.all(),
        empty_label = None,
        required = False
    )
    priority = forms.ModelChoiceField(
        label = "Priority",
        queryset = Priority.objects.all(),
        empty_label = None,
    )
    product = forms.ModelChoiceField(
        label = "Product",
        queryset = Product.objects.all(),
        empty_label = None,
    )
    category = forms.ModelChoiceField(
        label = "Category",
        queryset = TestCaseCategory.objects.none(),
        empty_label = None,
    )
    component = forms.ModelMultipleChoiceField(
        label = "Components",
        queryset = Component.objects.none(),
        required = False,
    )
    notes = forms.CharField(
        label='Notes',
        widget=forms.Textarea,
        required=False
    )
    estimated_time = TimedeltaFormField()
    setup = forms.CharField(label="Setup", widget = TinyMCEWidget, required = False)
    action = forms.CharField(label="Actions", widget = TinyMCEWidget, required = False)
    effect = forms.CharField(label="Expect results", widget = TinyMCEWidget, required = False)
    breakdown = forms.CharField(label="Breakdown", widget = TinyMCEWidget, required = False)

    tag = forms.CharField(
        label = "Tag",
        required = False
    )

    def clean_is_automated(self):
        data = self.cleaned_data['is_automated']
        if len(data) == 2:
            return 2

        if len(data):
            #FIXME: Should data always be a list?
            try:
                return int(data[0])
            except ValueError, e:
                return data[0]

        return data

    #def clean_alias(self):
    #    data = self.cleaned_data['alias']
    #    tc_count = TestCase.objects.filter(alias = data).count()
    #
    #    if tc_count == 0:
    #        return data
    #
    #    raise forms.ValidationError('Duplicated alias exist in database.')

    def clean_tag(self):
        tags = []
        if self.cleaned_data['tag']:
            tag_names = TestTag.string_to_list(self.cleaned_data['tag'])
            tags = TestTag.get_or_create_many_by_name(tag_names)
        return tags

    def populate(self, product_id = None):
        # We can dynamically set choices for a form field:
        # Seen at: http://my.opera.com/jacob7908/blog/2009/06/19/django-choicefield-queryset (Chinese)
        # Is this documented elsewhere?
        if hasattr(self, 'product') and self.product and not product_id:
            product = self.product

        if product_id:
            self.fields['category'].queryset = TestCaseCategory.objects.filter(product__id = product_id)
            self.fields['component'].queryset = Component.objects.filter(product__id = product_id)
        else:
            self.fields['category'].queryset = TestCaseCategory.objects.all()
            self.fields['component'].queryset = Component.objects.all()

class NewCaseForm(BaseCaseForm):
    def clean_case_status(self):
        if not self.cleaned_data['case_status']:
            return TestCaseStatus.get_PROPOSED()

        return self.cleaned_data['case_status']

class EditCaseForm(BaseCaseForm):
    pass

class CaseNotifyForm(forms.Form):
    author = forms.BooleanField(required = False)
    default_tester_of_case = forms.BooleanField(required = False)
    managers_of_runs = forms.BooleanField(required = False)
    default_testers_of_runs = forms.BooleanField(required = False)
    assignees_of_case_runs = forms.BooleanField(required = False)
    notify_on_case_update = forms.BooleanField(required=False)
    notify_on_case_delete = forms.BooleanField(required=False)

    cc_list = MultipleEmailField(
        required=False,
        label=u'CC to',
        help_text=u'It will send notification email to each Email address ' \
            'within CC list. Email addresses within CC list are ' \
            'separated by comma.',
        widget=forms.Textarea(attrs={ 'rows': 1, }))

# =========== Forms for  XML-RPC functions ==============

class XMLRPCBaseCaseForm(BaseCaseForm):
    estimated_time = forms.CharField(required = False)
    is_automated = forms.ChoiceField(
        choices = FULL_AUTOMATED_CHOICES,
        widget = forms.CheckboxSelectMultiple(),
        required = False,
    )

    def clean_estimated_time(self):
        et = self.cleaned_data['estimated_time']    # Estimated time

        if not et:
            return

        h, m, s = map(lambda x: int(x), et.split(':'))  # Hours, Minutes, Seconds
        s += SECONDS_PER_MIN * m
        s += SECONDS_PER_HOUR * h

        t = timedelta(seconds=s)
        return t

class XMLRPCNewCaseForm(XMLRPCBaseCaseForm):
    plan = forms.ModelMultipleChoiceField(
        label = 'Test Plan',
        queryset = TestPlan.objects.all(),
        required = False,
    )

    def clean_case_status(self):
        if not self.cleaned_data['case_status']:
            return TestCaseStatus.get_PROPOSED()

        return self.cleaned_data['case_status']

    def clean_is_automated(self):
        if self.cleaned_data['is_automated'] == '':
            return 0

        return self.cleaned_data['is_automated']

class XMLRPCUpdateCaseForm(XMLRPCBaseCaseForm):
    summary = forms.CharField(
        label = "Summary",
        required = False,
    )
    priority = forms.ModelChoiceField(
        label = "Priority",
        queryset = Priority.objects.all(),
        empty_label = None,
        required = False,
    )
    product = forms.ModelChoiceField(
        queryset = Product.objects.all(),
        empty_label = None,
        required = False,
    )
    category = forms.ModelChoiceField(
        queryset = TestCaseCategory.objects.none(),
        empty_label = None,
        required = False,
    )

# =========== Forms for search/filter ==============

class BaseCaseSearchForm(forms.Form):
    summary = forms.CharField(required=False)
    author = forms.CharField(required=False)
    default_tester = forms.CharField(required=False)
    tag__name__in = forms.CharField(required = False)
    category = forms.ModelChoiceField(
        label="Category",
        queryset=TestCaseCategory.objects.none(),
        required=False
    )
    priority = forms.ModelMultipleChoiceField(
        label="Priority",
        queryset=Priority.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )
    case_status = forms.ModelMultipleChoiceField(
        label="Case status",
        queryset=TestCaseStatus.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )
    component = forms.ModelChoiceField(
        label="Components",
        queryset=Component.objects.none(),
        required=False
    )
    bug_id = BugField(label="Bug ID", required=False)
    is_automated = forms.ChoiceField(
        choices = AUTOMATED_SERCH_CHOICES,
        required = False,
    )
    is_automated_proposed = forms.BooleanField(
        label = 'Autoproposed', required = False
    )

    def clean_bug_id(self):
        from tcms.core.utils import string_to_list
        data = self.cleaned_data['bug_id']
        data = string_to_list(data)
        for d in data:
            try:
                int(d)
            except ValueError, error:
                raise forms.ValidationError(error)

        return data

    def clean_tag__name__in(self):
        return TestTag.string_to_list(self.cleaned_data['tag__name__in'])

    def populate(self, product_id = None):
        """Limit the query to fit the plan"""
        if product_id:
            self.fields['category'].queryset = TestCaseCategory.objects.filter(product__id = product_id)
            self.fields['component'].queryset = Component.objects.filter(product__id = product_id)

class CaseFilterForm(BaseCaseSearchForm):
    pass

class SearchCaseForm(BaseCaseSearchForm):
    search = forms.CharField(required=False)
    plan = forms.CharField(required=False)
    product = forms.ModelChoiceField(
        label="Product",
        queryset=Product.objects.all(),
        required=False
    )

# =========== Mist Forms ==============

class CloneCaseForm(forms.Form):
    case = forms.ModelMultipleChoiceField(
        label = 'Test Case',
        queryset = TestCase.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )
    plan = forms.ModelMultipleChoiceField(
        label = 'Test Plan',
        queryset = TestPlan.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )
    copy_case = forms.BooleanField(
        label = 'Create a copy',
        help_text = 'Create a Copy (Unchecking will create a link to selected case)',
        required = False
    )
    maintain_case_orignal_author = forms.BooleanField(
        label = 'Keep original author',
        help_text = 'Keep original author(Unchecking will make me as author of the copied test case)',
        required = False
    )
    maintain_case_orignal_default_tester = forms.BooleanField(
        label = 'Keep original default tester',
        help_text = 'Keep original default tester(Unchecking will make me as default tester of the copied test case)',
        required = False
    )
    copy_component = forms.BooleanField(
        label = 'Copy the component to new product you specific',
        help_text = 'Copy the component to new product you specific (Unchecking will remove component of copied test case)',
        required = False
    )
    copy_attachment = forms.BooleanField(
        label = 'Copy the attachments',
        help_text = 'Copy the attachments to new product you specific (Unchecking will remove attachments of copied test case)',
        required = False
    )

    def populate(self, case_ids, plan = None):
        self.fields['case'].queryset = TestCase.objects.filter(case_id__in = case_ids)

class CaseAutomatedForm(forms.Form):
    a = forms.ChoiceField(
        choices = (('change', 'Change'),),
        widget = forms.HiddenInput(),
    )
    #case = forms.ModelMultipleChoiceField(
    #    queryset = TestCase.objects.none(),
    #    widget = forms.HiddenInput(),
    #)
    o_is_automated = forms.BooleanField(
        label = 'Automated', required = False,
        help_text = 'This is an automated test case.',
    )
    o_is_manual = forms.BooleanField(
        label = 'Manual', required = False,
        help_text = 'This is a manual test case.',
    )
    o_is_automated_proposed = forms.BooleanField(
        label = 'Autoproposed', required = False,
        help_text = 'This test case is planned to be automated.'
    )

    def clean(self):
        super(CaseAutomatedForm, self).clean()
        cdata = self.cleaned_data.copy() # Cleanen data

        cdata['is_automated'] = None
        cdata['is_automated_proposed'] = None

        if cdata['o_is_manual'] and cdata['o_is_automated']:
            cdata['is_automated'] = 2
        else:
            if cdata['o_is_manual']:
                cdata['is_automated'] = 0

            if cdata['o_is_automated']:
                cdata['is_automated'] = 1

        cdata['is_automated_proposed'] = cdata['o_is_automated_proposed']

        return cdata

    def populate(self):
        self.fields['case'].queryset = TestCase.objects.all()

class CaseBugForm(forms.ModelForm):
    case = forms.ModelChoiceField(
        queryset = TestCase.objects.all(),
        widget = forms.HiddenInput(),
    )
    case_run = forms.ModelChoiceField(
        queryset = TestCaseRun.objects.all(),
        widget = forms.HiddenInput(),
        required = False,
    )
    class Meta:
        model = TestCaseBug

class CaseComponentForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset = Product.objects.all(),
        empty_label = None,
        required = False,
    )
    #category = forms.ModelChoiceField(
    #    queryset = TestCaseCategory.objects.none(),
    #    empty_label = None,
    #    required = False,
    #)
    o_component = forms.ModelMultipleChoiceField(
        label = "Components",
        queryset = Component.objects.none(),
        required = False,
    )
    def populate(self, product_id = None):
        if product_id:
            #self.fields['category'].queryset = TestCaseCategory.objects.filter(product__id = product_id)
            self.fields['o_component'].queryset = Component.objects.filter(product__id = product_id)
        else:
            #self.fields['category'].queryset = TestCaseCategory.objects.all()
            self.fields['o_component'].queryset = Component.objects.all()

class CaseCategoryForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset = Product.objects.all(),
        empty_label = None,
        required = False,
    )
    #category = forms.ModelChoiceField(
    #    queryset = TestCaseCategory.objects.none(),
    #    empty_label = None,
    #    required = False,
    #)
    o_category = forms.ModelMultipleChoiceField(
        label = "Categorys",
        queryset = TestCaseCategory.objects.none(),
        required = False,
    )
    def populate(self, product_id = None):
        if product_id:
            #self.fields['category'].queryset = TestCaseCategory.objects.filter(product__id = product_id)
            self.fields['o_category'].queryset = TestCaseCategory.objects.filter(product__id = product_id)
        else:
            #self.fields['category'].queryset = TestCaseCategory.objects.all()
            self.fields['o_category'].queryset = TestCaseCategory.objects.all()

class CaseTagForm(forms.Form):
    o_tag = forms.ModelMultipleChoiceField(
        label="Tags",
        queryset=TestTag.objects.none(),
        required=False,
    )
    def populate(self, case_ids=None):
        if case_ids:
            self.fields['o_tag'].queryset = TestTag.objects.filter(testcase__in=case_ids).order_by('name').distinct()
        else:
            self.fields['o_category'].queryset = TestCaseCategory.objects.all()

