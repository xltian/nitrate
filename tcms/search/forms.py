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

# from django
from django import forms
# from tcms
from tcms.apps.management.models import Product, TestBuild, Component, Version
from tcms.apps.testcases.models import TestCaseCategory
from tcms.apps.testplans.models import TestPlanType
from tcms.search.utils import cached_entities
from tcms.apps.testcases.forms import BugField
# from stdlib
#from functools import partial

# temporary fix to the problem that python2.4 does not ship with a partial in functools
# seriously? Why the hell we'r still running 2.4?
def partial(func, **kwargs):
    def call(**xkwargs):
        kwargs.update(xkwargs)
        return func(**kwargs)
    return call

# template-functions creating form field with required = False
LooseCF     = partial(forms.CharField, required=False, max_length=200)
LooseIF     = partial(forms.IntegerField, required=False)
LooseBugF     = partial(BugField, required=False, max_length=200)
LooseDF     = partial(forms.DateField, required=False)
LooseBF     = partial(forms.BooleanField, required=False)
LooseMF     = partial(forms.MultipleChoiceField, required=False, choices=())
PlanTypeF   = partial(forms.ModelMultipleChoiceField, required=False, queryset=TestPlanType.objects.all())
ProductF    = partial(forms.ModelMultipleChoiceField, required=False, queryset=Product.objects.none())
BuildF      = partial(forms.ModelMultipleChoiceField, required=False, queryset=TestBuild.objects.none())
CategoryF   = partial(forms.ModelMultipleChoiceField, required=False, queryset=TestCaseCategory.objects.none())
ComponentF  = partial(forms.ModelMultipleChoiceField, required=False, queryset=Component.objects.none())
VersionF    = partial(forms.ModelMultipleChoiceField, required=False, queryset=Version.objects.none())

def get_choice(value, _type=str, deli=','):
    '''
    Used to clean a form field where multiple\n
    choices are seperated using a delimiter such as comma.\n
    Removing the empty value.
    '''
    try:
        results = value.split(deli)
        return [_type(r.strip()) for r in results if r]
    except Exception, e:
        raise forms.ValidationError(str(e))

def get_boolean_choice(value):
    return {
        'yes': True,
        'no': False
    }.get(value, None)

class PlanForm(forms.Form):
    pl_type         = PlanTypeF()
    pl_summary      = LooseCF()
    pl_id           = LooseCF()
    pl_authors      = LooseCF()
    pl_owners       = LooseCF()
    pl_tags         = LooseCF()
    pl_tags_exclude = LooseBF()
    pl_active       = LooseCF()
    pl_created_since  = LooseDF()
    pl_created_before = LooseDF()
    pl_product      = ProductF()
    pl_component    = ComponentF()
    pl_version      = VersionF()

    def clean_pl_active(self):
        return get_boolean_choice(self.cleaned_data['pl_active'])

    def clean_pl_id(self):
        return get_choice(self.cleaned_data['pl_id'], _type=int)

    def clean_pl_tags(self):
        return get_choice(self.cleaned_data['pl_tags'])

    def clean_pl_authors(self):
        return get_choice(self.cleaned_data['pl_authors'])

    def clean_pl_owners(self):
        return get_choice(self.cleaned_data['pl_owners'])

    def populate(self, data):
        prod_pks = data.getlist('pl_product')
        prod_pks = [k for k in prod_pks if k]
        if prod_pks:
            self.fields['pl_product'].queryset = Product.objects.filter(pk__in=prod_pks)
        comp_pks = data.getlist('pl_component')
        comp_pks = [k for k in comp_pks if k]
        if comp_pks:
            self.fields['pl_component'].queryset = Component.objects.filter(pk__in=comp_pks)
        ver_pks  = data.getlist('pl_version')
        ver_pks = [k for k in ver_pks if k]
        if ver_pks:
            self.fields['pl_version'].queryset = Version.objects.filter(pk__in=ver_pks)

class CaseForm(forms.Form):
    STATUS_CHOICE = [
        (s.pk, s.name) for s in cached_entities('TestCaseStatus')
    ]
    PRIORITY_CHOICE = [
        (p.pk, p.value) for p in cached_entities('Priority')
    ]
    cs_id       = LooseCF()
    cs_summary  = LooseCF()
    cs_authors  = LooseCF()
    cs_tester   = LooseCF()
    cs_tags     = LooseCF()
    cs_bugs     = LooseBugF()
    cs_status   = LooseMF(choices=STATUS_CHOICE)
    cs_priority = LooseMF(choices=PRIORITY_CHOICE)
    cs_auto     = LooseCF()
    cs_proposed = LooseCF()
    cs_script   = LooseCF()
    cs_created_since  = LooseDF()
    cs_created_before = LooseDF()
    cs_tags_exclude   = LooseBF()
    cs_product   = ProductF()
    cs_component = ComponentF()
    cs_category  = CategoryF()

    def clean_cs_auto(self):
        return get_boolean_choice(self.cleaned_data['cs_auto'])

    def clean_cs_proposed(self):
        return get_boolean_choice(self.cleaned_data['cs_proposed'])

    def clean_cs_id(self):
        return get_choice(self.cleaned_data['cs_id'], _type=int)

    def clean_cs_authors(self):
        return get_choice(self.cleaned_data['cs_authors'])

    def clean_cs_bugs(self):
        return get_choice(self.cleaned_data['cs_bugs'], int)

    def clean_cs_tags(self):
        return get_choice(self.cleaned_data['cs_tags'])

    def clean_cs_tester(self):
        return get_choice(self.cleaned_data['cs_tester'])

    def populate(self, data):
        prod_pks = data.getlist('cs_product')
        prod_pks = [k for k in prod_pks if k]
        if prod_pks:
            self.fields['cs_product'].queryset = Product.objects.filter(pk__in=prod_pks)
        comp_pks = data.getlist('cs_component')
        comp_pks = [k for k in comp_pks if k]
        if comp_pks:
            self.fields['cs_component'].queryset = Component.objects.filter(pk__in=comp_pks)
        cat_pks  = data.getlist('cs_category')
        cat_pks = [k for k in cat_pks if k]
        if cat_pks:
            self.fields['cs_category'].queryset = TestCaseCategory.objects.filter(pk__in=cat_pks)

class RunForm(forms.Form):
    r_id        = LooseCF()
    r_summary   = LooseCF()
    r_manager   = LooseCF()
    r_tester    = LooseCF()
    r_tags      = LooseCF()
    r_running   = LooseCF()
    r_begin     = LooseDF()
    r_finished  = LooseDF()
    r_created_since  = LooseDF()
    r_created_before = LooseDF()
    r_tags_exclude   = LooseBF()
    r_real_tester    = LooseCF()
    r_build     = BuildF()
    r_product   = ProductF()
    r_version   = VersionF()

    def clean_r_running(self):
        return get_boolean_choice(self.cleaned_data['r_running'])

    def clean_r_id(self):
        return get_choice(self.cleaned_data['r_id'], _type=int)

    def clean_r_tags(self):
        return get_choice(self.cleaned_data['r_tags'])

    def clean_r_tester(self):
        return get_choice(self.cleaned_data['r_tester'])

    def clean_r_real_tester(self):
        return get_choice(self.cleaned_data['r_real_tester'])

    def clean_r_manager(self):
        return get_choice(self.cleaned_data['r_manager'])

    def clean_r_version(self):
        # run.product_version is not a foreignkey
        versions = self.cleaned_data['r_version']
        if versions:
            versions = versions.values_list('value', flat=True)
        return versions

    def populate(self, data):
        prod_pks = data.getlist('r_product')
        prod_pks = [k for k in prod_pks if k]
        if prod_pks:
            self.fields['r_product'].queryset = Product.objects.filter(pk__in=prod_pks)
        build_pks = data.getlist('r_build')
        build_pks = [k for k in build_pks if k]
        if build_pks:
            self.fields['r_build'].queryset = TestBuild.objects.filter(pk__in=build_pks)
        ver_pks  = data.getlist('r_version')
        ver_pks = [k for k in ver_pks if k]
        if ver_pks:
            self.fields['r_version'].queryset = Version.objects.filter(pk__in=ver_pks)
