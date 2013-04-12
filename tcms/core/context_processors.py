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

def admin_prefix_processor(request):
    """
    Django Admin URL Prefix RequestContext Handler
    """
    return { 'ADMIN_PREFIX': settings.ADMIN_PREFIX }

def admin_media_prefix_processor(request):
    """
    Django Admin Media URL Prefix RequestContext Handler
    """
    return { 'ADMIN_MEDIA_PREFIX': settings.ADMIN_MEDIA_PREFIX }

def auth_backend_processor(request):
    """Determine the be able to login/logout/register request """
    from tcms.core.contrib.auth import get_using_backend
    return { 'AUTH_BACKEND': get_using_backend() }

def request_contents_processor(request):
    """
    Django request contents RequestContext Handler
    """
    return { 'REQUEST_CONTENTS': request.REQUEST }

def settings_processor(request):
    """
    Django settings RequestContext Handler
    """
    return { 'SETTINGS': settings }
