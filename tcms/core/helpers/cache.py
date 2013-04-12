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
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache

def cached_entities(ctype_name):
    '''
    Some entities are frequently used.\n
    Cache them for reuse.\n
    Retrieve using model names.
    '''
    ctype_key   = 'ctt_type_' + ctype_name
    c_type      = cache.get(ctype_key)
    if not c_type:
        c_type  = ContentType.objects.get(model__iexact=ctype_name)
        cache.set(ctype_key, c_type)
    model_class = c_type.model_class()
    key         = 'cached_' + ctype_name
    entities    = cache.get(key)
    if not entities:
        entities    = model_class._default_manager.all()
        cache.set(key, entities)
    return entities
