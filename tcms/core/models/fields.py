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

# Suppress warning about string statement:
# pylint: disable-msg=W0105

import datetime

from django.db import models
from django.db.backends.mysql.base import django_conversions
from django.conf import settings

from MySQLdb.constants import FIELD_TYPE

from tcms.core.forms import TimedeltaFormField, SECONDS_PER_DAY, SECONDS_PER_HOUR, SECONDS_PER_MIN

django_conversions.update({FIELD_TYPE.TIME: None})

class TimedeltaField(models.Field):
    u'''
    Store Python's datetime.timedelta in an integer column.
    Most databasesystems only support 32 Bit integers by default.
    '''
    __metaclass__=models.SubfieldBase
    def __init__(self, *args, **kwargs):
        super(TimedeltaField, self).__init__(*args, **kwargs)
    
    def to_python(self, value):
        if (value is None) or value == '':
            return datetime.timedelta(seconds=0)
        
        if isinstance(value, datetime.timedelta):
            return value
        
        if isinstance(value, str):
            hours, minutes, seconds = map(int, value.split(':'))
            total_seconds = seconds + (60 * (minutes + (60 * hours)))
            return datetime.timedelta(seconds=total_seconds)
        
        assert isinstance(value, int), (value, type(value))
        return datetime.timedelta(seconds=value)
    
    def get_internal_type(self):
        return 'IntegerField'
    
    def get_db_prep_lookup(self, lookup_type, value):
        raise NotImplementedError()  # SQL WHERE
    
    def get_db_prep_save(self, value):
        if (value is None) or value == '':
            return '00:00:00'
        
        if isinstance(value, int):
            value = datetime.timedelta(seconds=value)
        
        if isinstance(value, datetime.timedelta):
            total_seconds = value.seconds + (value.days * SECONDS_PER_DAY)
            return '%02i:%02i:%02i' % (
                total_seconds / SECONDS_PER_HOUR, # hours
                # minutes - Total seconds subtract the used hours
                total_seconds / SECONDS_PER_MIN - total_seconds / SECONDS_PER_HOUR * 60,
                total_seconds % SECONDS_PER_MIN # seconds
            )
        
        return SECONDS_PER_DAY*value.days+value.seconds
    
    def formfield(self, *args, **kwargs):
        defaults={'form_class': TimedeltaFormField}
        defaults.update(kwargs)
        return super(TimedeltaField, self).formfield(*args, **defaults)

class BlobValueWrapper(object):
    """
    Wrap the blob value so that we can override the unicode method.
    After the query succeeds, Django attempts to record the last query
    executed, and at that point it attempts to force the query string
    to unicode. This does not work for binary data and generates an
    uncaught exception.
    """
    def __init__(self, val):
        self.val = val
    
    def __str__(self):
        return self.val
    
    def __unicode__(self):
        return u'blobdata_unicode'

class BlobField(models.Field):
    """A field for persisting binary data in databases that we support."""
    __metaclass__ = models.SubfieldBase
    
    def db_type(self):
        if settings.DATABASE_ENGINE == 'mysql':
            return 'LONGBLOB'
        elif settings.DATABASE_ENGINE == 'postgresql_psycopg2':
            return 'bytea'
        elif settings.DATABASE_ENGINE == 'sqlite3':
            return 'bytea'
        else:
            raise NotImplementedError
    
    def to_python(self, value):
        if settings.DATABASE_ENGINE == 'postgresql_psycopg2':
            if value is None:
                return value
            return str(value)
        else:
            return value
    
    def get_db_prep_save(self, value):
        if value is None:
            return None
        if settings.DATABASE_ENGINE =='postgresql_psycopg2':
            return psycopg2.Binary(value)
        else:
            return str(value)
