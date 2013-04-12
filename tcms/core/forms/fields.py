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
from django.db.models import Q
from django.forms import ValidationError
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from tcms.core.utils import string_to_list

from widgets import *

class UserField(forms.CharField):
    """
    Custom field type.
    Will eventually support user selection
    """
    def clean(self, value):
        """
        Form-validation:  accept a string/integer.
        Looks at both email address and real name.
        """
        if value == '' or value is None:
            if self.required:
                raise ValidationError('A user name or user ID is required.')
            else:
                return None
        if isinstance(value, int):
            try:
                return User.objects.get(pk=value)
            except User.DoesNotExist:
                raise ValidationError('Unknown user_id: "%s"' % value)
        else:
            value = value.strip()
            if value.isdigit():
                try:
                    return User.objects.get(pk=value)
                except User.DoesNotExist:
                    raise ValidationError('Unknown user_id: "%s"' % value)
            else:
                try:
                    return User.objects.get((Q(email=value) | Q(username=value)))
                except User.DoesNotExist:
                    raise ValidationError('Unknown user: "%s"' % value)


class TimedeltaFormField(forms.Field):
    default_error_messages = {
        'invalid':  _(u'Enter a whole number.'),
        }

    def __init__(self, *args, **kwargs):
        defaults={'widget': TimedeltaWidget}
        defaults.update(kwargs)
        super(TimedeltaFormField, self).__init__(*args, **defaults)

    def clean(self, value):
        # value comes from Timedelta.Widget.value_from_datadict(): tuple of strings
        super(TimedeltaFormField, self).clean(value)
        assert len(value)==len(self.widget.inputs), (value, self.widget.inputs)
        i=0
        for value, multiply in zip(value, self.widget.multiply):
            try:
                i+=int(value)*multiply
            except ValueError, TypeError:
                raise forms.ValidationError(self.error_messages['invalid'])
        return i

class MultipleEmailField(forms.EmailField):
    def clean(self, value):
        """
        Validates that the input matches the regular expression. Returns a
        Unicode object.
        """
        value = super(forms.CharField, self).clean(value)
        if value == u'':
            return value

        return [v for v in string_to_list(strs = value) if self.regex.search(v)]
