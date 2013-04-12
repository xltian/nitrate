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

from django.db import models
from django.contrib.auth.models import User
from fields import TimedeltaField, BlobValueWrapper, BlobField
from base import TCMSContentTypeBaseModel, UrlMixin

from tcms.core.utils.xmlrpc import XMLRPCSerializer
from tcms.core.logs.views import TCMSLog

User._meta.ordering = ['username']

class TCMSActionModel(models.Model, UrlMixin):
    """
    TCMS action models.
    Use for global log system.
    """
    class Meta:
        abstract = True
    
    @classmethod
    def to_xmlrpc(cls, query = {}):
        """
        Convert the query set for XMLRPC
        """
        s = XMLRPCSerializer(queryset = cls.objects.filter(**query))
        return s.serialize_queryset()
    
    def serialize(self):
        """
        Convert the model for XMLPRC
        """
        s = XMLRPCSerializer(model = self)
        return s.serialize_model()
    
    def log(self):
        log = TCMSLog(model = self)
        return log.list()
    
    def log_action(self, who, action):
        log = TCMSLog(model = self)
        log.make(who = who, action = action)
        
        return log
