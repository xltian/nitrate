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

from django.conf import settings
from django import forms
from django.contrib.comments.forms import CommentDetailsForm
from django.utils.translation import ungettext, ugettext_lazy as _

COMMENT_MAX_LENGTH = getattr(settings,'COMMENT_MAX_LENGTH', 10000)

class SimpleForm(CommentDetailsForm):
    name = forms.CharField(
        label=_("Name"), widget=forms.HiddenInput, max_length=50,
        required=False,
    )
    email = forms.EmailField(
        label=_("Email address"), widget=forms.HiddenInput, required=False
    )
    url = forms.URLField(
        label=_("URL"), widget=forms.HiddenInput,
        required=False
    )
    comment = forms.CharField(
        label=_('Comment'),
        widget=forms.Textarea,
        max_length=COMMENT_MAX_LENGTH,
    )
    
    def clean_timestamp(self):

        #return self.cleaned_data["timestamp"]

        import time
        return str(time.time()).split('.')[0]
    
    def get_form(self):
        # Use our custom comment model instead of the built-in one.
        return SimpleForm
