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

from tcms.apps.management.models import TCMSEnvGroup, TCMSEnvProperty, TCMSEnvValue
from utils import pre_process_ids

__all__ = (
    'filter_groups',
    'filter_properties',
    'filter_values',
    'get_properties',
    'get_values',
)

def filter_groups(request, query):
    """
    Description: Performs a search and returns the resulting list of env groups.

    Params:      $query - Hash: keys must match valid search fields.

    +------------------------------------------------------------------+
    |               Product Search Parameters                          |
    +------------------------------------------------------------------+
    |        Key          |          Valid Values                      |
    | id                  | Integer: ID of env group                   |
    | name                | String                                     |
    | manager             | ForeignKey: Auth.user                      |
    | modified_by         | ForeignKey: Auth.user                      |
    | is_active           | Boolean                                    |
    | property            | ForeignKey: TCMSEnvProperty                |
    +------------------------------------------------------------------+

    Returns:     Array: Matching env groups are retuned in a list of hashes.

    Example:
    # Get all of env group name contains 'Desktop'
    >>> Env.filter_groups({'name__icontains': 'Desktop'})
    """
    return TCMSEnvGroup.to_xmlrpc(query)

def filter_properties(request, query):
    """
    Description: Performs a search and returns the resulting list of env properties.

    Params:      $query - Hash: keys must match valid search fields.

    +------------------------------------------------------------------+
    |               Product Search Parameters                          |
    +------------------------------------------------------------------+
    |        Key          |          Valid Values                      |
    | id                  | Integer: ID of env properties              |
    | name                | String                                     |
    | is_active           | Boolean                                    |
    | group               | ForeignKey: TCMSEnvGroup                   |
    | value               | ForeignKey: TCMSEnvValues                   |
    +------------------------------------------------------------------+

    Returns:     Array: Matching env properties are retuned in a list of hashes.

    Example:
    # Get all of env properties name contains 'Desktop'
    >>> Env.filter_properties({'name__icontains': 'Desktop'})
    """
    return TCMSEnvProperty.to_xmlrpc(query)

def filter_values(request, query):
    """
    Description: Performs a search and returns the resulting list of env properties.

    Params:      $query - Hash: keys must match valid search fields.

    +------------------------------------------------------------------+
    |               Product Search Parameters                          |
    +------------------------------------------------------------------+
    |        Key          |          Valid Values                      |
    | id                  | Integer: ID of env value                   |
    | value               | String                                     |
    | is_active           | Boolean                                    |
    | property            | ForeignKey: TCMSEnvProperty                |
    +------------------------------------------------------------------+

    Returns:     Array: Matching env values are retuned in a list of hashes.

    Example:
    # Get all of env values name contains 'Desktop'
    >>> Env.filter_values({'name__icontains': 'Desktop'})
    """
    return TCMSEnvValue.to_xmlrpc(query)

def get_properties(request, env_group_id = None, is_active = True):
    """
    Description: Get the list of properties associated with this env group.

    Params:      $env_group_id - Integer: env_group_id of the env group in the Database
                                 Return all of properties when the argument is not specific.
                 $is_active    - Boolean: True to only include builds where is_active is true.
                                 Default: True
    Returns:     Array: Returns an array of env properties objects.

    Example:
    # Get all of properties
    >>> Env.get_properties()
    # Get the properties in group 10
    >>> Env.get_properties(10)
    """
    query = { 'is_active': is_active }
    if env_group_id: query['group__pk'] = env_group_id

    return TCMSEnvProperty.to_xmlrpc(query)

def get_values(request, env_property_id = None, is_active = True):
    """
    Description: Get the list of values associated with this env property.

    Params:      $env_property_id - Integer: env_property_id of the env property in the Database
                                    Return all of values when the argument is not specific.
                 $is_active       - Boolean: True to only include builds where is_active is true.
                                    Default: True
    Returns:     Array: Returns an array of env values objects.

    Example:
    # Get all of properties
    >>> Env.get_properties()
    # Get the properties in group 10
    >>> Env.get_properties(10)
    """
    query = { 'is_active': is_active }
    if env_property_id: query['property__pk'] = env_property_id

    return TCMSEnvValue.to_xmlrpc(query)
