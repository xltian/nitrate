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
#   Chenxiong Qi <cqi@redhat.com>

from itertools import ifilterfalse

from django.forms import EmailField
from django.forms import ValidationError
from django.forms import Textarea

__all__ = [ 'MultipleEmailField', 'CC_LIST_DEFAULT_DELIMITER', ]

CC_LIST_DEFAULT_DELIMITER = ','

class MultipleEmailField(EmailField):
    ''' Holding mulitple email addresses '''

    default_error_messages = {
        'invalid': u'%(value)s is/are not valid email addresse(s).',
    }

    def __init__(self, delimiter=CC_LIST_DEFAULT_DELIMITER, *args, **kwargs):

        super(MultipleEmailField, self).__init__(*args, **kwargs)
        self.delimiter = delimiter

    def to_python(self, value):

        if not value:
            return []

        if not isinstance(value, unicode):
            raise ValidationError(
                '%s is not a valid string value.' % str(value))

        result = [item.strip() for item in ifilterfalse(
            lambda item: item.strip() == '', value.split(self.delimiter))]
        return result

    def clean(self, value):
        email_addrs = self.to_python(value)
        super_instance = super(MultipleEmailField, self)

        valid_email_addrs = []
        invalid_email_addrs = []

        self.validate(email_addrs)

        for email_addr in email_addrs:
            try:
                super_instance.run_validators(email_addr)
            except ValidationError, err:
                invalid_email_addrs.append(email_addr)
            else:
                valid_email_addrs.append(email_addr)

        if invalid_email_addrs:
            raise ValidationError(
                self.error_messages['invalid'] % {
                    'value': ', '.join(invalid_email_addrs) })

        return valid_email_addrs
