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

from django import template

register = template.Library()

@register.filter(name='cutbystring')
def cut_by_string(value, arg):
    arg = int(arg)
    if len(value) < arg:
        return value
    else:
        return value[:arg-3] + "..."

@register.filter(name='ismine')
def is_mine(object, user):
    if hasattr(object, 'author') and object.author == user: return True
    if hasattr(object, 'manager') and object.manager == user: return True
    
    return False

@register.filter(name='smart_unicode')
def smart_unicode(object):
    from django.utils.encoding import smart_unicode
    if not object:
        return object
    return smart_unicode(object)

@register.filter(name='smart_int')
def smart_int(object):
    if not object:
        return object
    
    try:
        return int(object)
    except ValueError:
        return object

#@register.filter(name='absolute_url')
@register.inclusion_tag('mail/new_run.txt', takes_context = True)
def absolute_url(context):
    request = context['request']
    object = context['test_run']
    if not hasattr(object, 'get_absolute_url'):
        return None
    
    return object.get_absolute_url(request)

