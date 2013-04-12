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

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

from kobo.django.xmlrpc.decorators import user_passes_test, login_required, log_call

from tcms.core.utils.xmlrpc import XMLRPCSerializer

__all__ = (
    'filter',
    'get',
    'get_me',
    'update',
)

def get_user_dict(user):
    u = XMLRPCSerializer(model = user)
    u = u.serialize_model()
    if u.get('password'):
        del u['password']
    return u

@log_call
def filter(request, query):
    """
    Description: Performs a search and returns the resulting list of test cases.

    Params:      $query - Hash: keys must match valid search fields.

        +------------------------------------------------------------------+
        |                 Case Search Parameters                           |
        +------------------------------------------------------------------+
        |        Key          |          Valid Values                      |
        | id                  | Integer: ID                                |
        | username            | String: User name                          |
        | first_name          | String: User first name                    |
        | last_name           | String: User last  name                    |
        | email               | String Email                               |
        | is_active           | Boolean: Return the active users           |
        | groups              | ForeignKey: AuthGroup                      |
        +------------------------------------------------------------------+

    Returns:     Array: Matching test cases are retuned in a list of hashes.

    Example:
    >>> User.filter({'username__startswith': 'x'})
    """
    users = User.objects.filter(**query)
    return [get_user_dict(u) for u in users]

def get(request, id):
    """
    Description: Used to load an existing test case from the database.

    Params:      $id - Integer/String: An integer representing the ID in the database

    Returns:     A blessed User object Hash

    Example:
    >>> User.get(2206)
    """
    return get_user_dict(User.objects.get(pk = id))

def get_me(request):
    """
    Description: Get the information of myself.

    Returns:     A blessed User object Hash

    Example:
    >>> User.get_me()
    """
    return get_user_dict(request.user)

def update(request, values = {}, id = None):
    """
    Description: Updates the fields of the selected user. it also can change the
                 informations of other people if you have permission.
    
    Params:      $values   - Hash of keys matching TestCase fields and the new values 
                             to set each field to.

                 $id       - Integer/String(Optional)
                             Integer: A single TestCase ID.
                             String:  A comma string of User ID.
                             Default: The ID of myself

    Returns:     A blessed User object Hash

    +-------------------+----------------+-----------------------------------------+
    | Field             | Type           | Null                                    |
    +-------------------+----------------+-----------------------------------------+
    | first_name        | String         | Optional                                |
    | last_name         | String         | Optional(Required if changes category)  |
    | email             | String         | Optional                                |
    | password          | String         | Optional                                |
    | old_password      | String         | Required by password                    |
    +-------------------+----------------+-----------------------------------------+

    Example:
    >>> User.update({'first_name': 'foo'})
    >>> User.update({'password': 'foo', 'old_password': '123'})
    >>> User.update({'password': 'foo', 'old_password': '123'}, 2206)
    """
    if id:
        u = User.objects.get(pk = id)
    else:
        u = request.user
    
    editable_fields = ['first_name', 'last_name', 'email', 'password']
    
    if not request.user.has_perm('auth.change_changeuser') and request.user != u:
        raise PermissionDenied
        
    for f in editable_fields:
        if values.get(f):
            if f == 'password':
                if not request.user.has_perm('auth.change_changeuser') and not values.get('old_password'):
                    raise PermissionDenied('Old password is required')
                    
                if not request.user.has_perm('auth.change_changeuser') and not u.check_password(values.get('old_password')):
                    raise PermissionDenied('Password is incorrect')
                
                u.set_password(values['password'])
            else:
                setattr(u, f, values[f])
            
    u.save()
    return get_user_dict(u)
