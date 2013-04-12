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

from django import forms

from tcms.apps.management.models import Component, Product, TestBuild, Version
from tcms.apps.testcases.models import TestCaseCategory

class CustomSearchForm(forms.Form):
    pk__in = forms.ModelMultipleChoiceField(
        label = 'Build',
        queryset = TestBuild.objects.none(),
        required = False,
    )
    product = forms.ModelChoiceField(
        label = 'Product',
        queryset = Product.objects.all(),
    )
    build_run__product_version = forms.ModelChoiceField(
        label = 'Product version',
        queryset = Version.objects.none(),
        required = False,
    )
    build_run__plan__name__icontains = forms.CharField(
        label = 'Plan name',
        required = False,
    )
    testcaserun__case__category = forms.ModelChoiceField(
        label = 'Case category',
        queryset = TestCaseCategory.objects.none(),
        required = False,
    )
    testcaserun__case__component = forms.ModelChoiceField(
        label = 'Case component',
        queryset = Component.objects.none(),
        required = False,
    )

    def populate(self, product_id):
        if product_id:
            self.fields['build_run__product_version'].queryset = Version.objects.filter(product__id = product_id)
            self.fields['pk__in'].queryset = TestBuild.objects.filter(product__id = product_id)
            self.fields['testcaserun__case__category'].queryset = TestCaseCategory.objects.filter(product__id = product_id)
            self.fields['testcaserun__case__component'].queryset = Component.objects.filter(product__id = product_id)
        else:
            self.fields['build_run__product_version'].queryset = Version.objects.all()
            self.fields['pk__in'].queryset = TestBuild.objects.all()
            self.fields['testcaserun__case__category'].queryset = TestCaseCategory.objects.all()
            self.fields['testcaserun__case__component'].queryset = Component.objects.all()

    def clean_build_run__product_version(self):
        cleaned_data = self.cleaned_data['build_run__product_version']
        if cleaned_data:
            return cleaned_data.value

        return cleaned_data

class CustomSearchDetailsForm(CustomSearchForm):
    pk__in = forms.ModelChoiceField(
        label = 'Build',
        queryset = TestBuild.objects.none(),
    )

    #FIXME: Remove version from custom report due to data inconsistency.
    #See https://bugzilla.redhat.com/show_bug.cgi?id=678203
    def clean_build_run__product_version(self):
        return None
