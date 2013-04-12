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
from models import TestReview
from tcms.core.forms import UserField
from tcms.apps.management.models import TestBuild
from tcms.apps.testcases.models import TestCase

from models import TestReviewCase

class NewReviewForm(forms.ModelForm):
    default_reviewer = UserField(required=False)
    case = forms.ModelMultipleChoiceField(
        queryset = TestCase.objects.all()
    )

    class Meta:
        model = TestReview
        exclude = ('plan', 'author')

    def __init__(self, author, plan, *args, **kwargs):
        super(NewReviewForm, self).__init__(*args, **kwargs)
        self.plan = plan
        self.author = author
        query = {'product_id': self.plan.product_id}
        self.fields['build'].queryset = TestBuild.list_active(query)
