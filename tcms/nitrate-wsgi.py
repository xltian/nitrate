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

"""
Nitrate WSGI Handler.

Based on http://code.google.com/p/modwsgi/wiki/IntegrationWithDjango
"""

import os
import django.core.handlers.wsgi

# add tcms's core lib path
import tcms, sys
# tcms should exist in only one path.
sys.path.append(os.path.join(tcms.__path__[0], 'core', 'lib'))

os.environ['PYTHON_EGG_CACHE'] = '/tmp/.python-eggs/'
os.environ['DJANGO_SETTINGS_MODULE'] = 'tcms.product_settings'

_application = django.core.handlers.wsgi.WSGIHandler()

def application(environ, start_response):
    environ['PATH_INFO'] = environ['SCRIPT_NAME'] + environ['PATH_INFO']
    if environ['wsgi.url_scheme'] == 'https':
        environ['HTTPS'] = 'on'
    
    return _application(environ, start_response)
