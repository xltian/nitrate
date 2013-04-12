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
from django.utils.safestring import mark_safe, SafeData
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def split_as_option(value, splitter='|', autoescape=None):
    if not isinstance(value, SafeData):
        value = mark_safe(value)
    value = value.split(splitter)
    result = ""

    for v in value:
        result += '<option value="%s">%s</option>\n' % (v, v)

    return mark_safe(result)
split_as_option.is_safe = True
split_as_option.needs_autoescape = True

@register.filter
@stringfilter
def split_as_value(value, splitter='|', autoescape=None):
    if not isinstance(value, SafeData):
        value = mark_safe(value)
    value = value.split(splitter)
    result = ""

    for v in value:
        result += '<span class="value">%s</span>' % v

    return mark_safe(result)
split_as_value.is_safe = True
split_as_value.needs_autoescape = True

@register.filter
@stringfilter
def split_as_inputbox(value, splitter='|', autoescape=None):
    if not isinstance(value, SafeData):
        value = mark_safe(value)
    value = value.split(splitter)
    result = ""

    for v in value:
        result += '<input id="id_btn_%s" type="text" name="value" value="%s" /><input type="button" value="Del" onclick="$(\'id_btn_%s\').remove(); this.remove();" />' % (v, v, v)

    return mark_safe(result)
split_as_inputbox.is_safe = True
split_as_inputbox.needs_autoescape = True
