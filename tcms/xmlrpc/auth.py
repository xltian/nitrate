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

import django.contrib.auth
from django.conf import settings
from django.core.exceptions import PermissionDenied

__all__ = (
    'login', 'logout', 'login_krbv'
)

def check_user_name(parameters):
    username = parameters.get('username')
    password = parameters.get('password')
    if not username or not password:
        raise PermissionDenied('Username and password is required')
    
    return username, password

def login(request, parameters):
    """
    Description: Login into Nitrate
    Params:      $parameters - Hash: keys must match valid search fields.
    +-------------------------------------------------------------------+
    |                    Login Parameters                               |
    +-------------------------------------------------------------------+
    |        Key          |          Valid Values                       |
    | username            | A nitrate login (email address)             |
    | password            | String                                      |
    +-------------------------------------------------------------------+
    
    Returns:     String: Session ID.
    
    Example:
    >>> Auth.login({'username': 'foo', 'password': 'bar'})
    """
    from tcms.core.contrib.auth import get_backend
    user = None
    
    for backend_str in settings.AUTHENTICATION_BACKENDS:
        backend = get_backend(backend_str)
        user = backend.authenticate(*check_user_name(parameters))
        
        if user:
            user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            django.contrib.auth.login(request, user)
            return request.session.session_key
            
    if user is None:
        raise PermissionDenied('Wrong username or password')

def login_krbv(request):
    """
    Description: Login into the Nitrate deployed with mod_auth_kerb

    Returns:     String: Session ID.
    
    Example:
    $ kinit
    Password for username@example.com:

    $ python
    >>> Auth.login_krbv()
    """
    from django.contrib.auth.middleware import RemoteUserMiddleware

    middleware = RemoteUserMiddleware()
    user = middleware.process_request(request)

    return request.session.session_key

def logout(request):
    """Description: Delete session information."""
    django.contrib.auth.logout(request)
    return

