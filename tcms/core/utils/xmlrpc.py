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

import datetime

from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.db.models import ObjectDoesNotExist
from tcms.core.forms.widgets import SECONDS_PER_MIN, SECONDS_PER_HOUR, SECONDS_PER_DAY

class XMLRPCSerializer(object):
    """
    Django XMLRPC Serializer
    The goal is to process the datetime and timedelta data structure
    that python xmlrpclib can not handle.
    
    How to use it:
    # Model
    m = Model.objects.get(pk = 1)
    s = XMLRPCSerializer(model = m)
    s.serialize()
    
    Or
    # QuerySet
    q = Model.objects.all()
    s = XMLRPCSerializer(queryset = q)
    s.serialize()
    """
    def __init__(self, queryset=None, model=None):
        """Initial the class"""
        if hasattr(queryset, '__iter__'):
            self.queryset = queryset
            return
        elif hasattr(model, '__dict__'):
            self.model = model
            return
        
        raise TypeError("QuerySet(list) or Models(dictionary) is required")
   
   #FIXME: infinit loop here
   #def serialize(self):
   #     if hasattr(self, 'queryset'):
   #         return self.serialize_queryset()
   #         
   #     if hasattr(self, 'model'):
   #         return self.serialize_model()
    
    def serialize_model(self):
        """
        Check the fields of models and convert the data
        
        Returns: Dictionary
        """
        if not hasattr(self.model, '__dict__'):
            raise TypeError("Models or Dictionary is required")
        response = {}
        opts = self.model._meta
        for field in opts.local_fields:
            # for a django model, retrieving a foreignkey field
            # will fail when the field value isn't set
            try:
                value = getattr(self.model, field.name)
            except ObjectDoesNotExist:
                value = None
            if isinstance(value, datetime.datetime):
                value = datetime.datetime.strftime(value, "%Y-%m-%d %H:%M:%S")
            if isinstance(value, datetime.timedelta):
                total_seconds = value.seconds + (value.days * SECONDS_PER_DAY)
                value = '%02i:%02i:%02i' % (
                    total_seconds / SECONDS_PER_HOUR, # hours
                    # minutes - Total seconds subtract the used hours
                    total_seconds / SECONDS_PER_MIN - total_seconds / SECONDS_PER_HOUR * 60,
                    total_seconds % SECONDS_PER_MIN # seconds
                )
            if isinstance(field, ForeignKey):
                fk_id = "%s_id" % field.name
                if value is None:
                    response[fk_id] = None
                else:
                    response[fk_id] = getattr(self.model, fk_id)
                    value = str(value)
            response[field.name] = value
        for field in opts.local_many_to_many:
            value = getattr(self.model, field.name)
            value = value.values_list('pk', flat=True)
            response[field.name] = list(value)
        return response

    def serialize_queryset(self):
        """
        Check the fields of QuerySet and convert the data
        
        Returns: List
        """
        response = []
        for m in self.queryset:
            self.model = m
            m = self.serialize_model()
            response.append(m)
            
        del self.queryset
        return response

if __name__ == '__main__':
    import xmlrpclib
    
    VERBOSE = 0
    
    server = xmlrpclib.ServerProxy(
        'http://localhost:8080/xmlrpc/',
        verbose = VERBOSE
    )
    
    print server.TestRun.get_test_case_runs(137)
