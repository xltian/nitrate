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

from kobo.django.xmlrpc.decorators import user_passes_test, login_required, log_call
from tcms.apps.management.models import Product, TestBuild
from utils import pre_check_product

__all__ = (
    'check_build', 'create', 'get', 'get_runs', 'get_caseruns',
    'lookup_id_by_name', 'lookup_name_by_id', 'update'
)

def check_build(request, name, product):
    """
    Description: Looks up and returns a build by name.

    Params:      $name - String: name of the build.
                 $product - product_id of the product in the Database

    Returns:     Hash: Matching Build object hash or error if not found.

    Example:
    # Get with product ID
    >>> Build.check_build('2008-02-25', 61)
    # Get with product name
    >>> Build.check_build('2008-02-25', 'Red Hat Enterprise Linux 5')
    """
    p = pre_check_product(values = product)
    try:
        tb = TestBuild.objects.get(name = name, product = p)
    except TestBuild.DoesNotExist, error:
        return error

    return tb.serialize()

@log_call
@user_passes_test(lambda u: u.has_perm('management.add_testbuild'))
def create(request, values):
    """
    Description: Creates a new build object and stores it in the database

    Params:      $values - Hash: A reference to a hash with keys and values
                 matching the fields of the build to be created.

        +-------------+----------------+-----------+---------------------------+
        | Field       | Type           | Null      | Description               |
        +-------------+----------------+-----------+---------------------------+
        | product     | Integer/String | Required  | ID or Name of product     |
        | name        | String         | Required  |                           |
        | description | String         | Optional  |                           |
        | is_active   | Boolean        | Optional  | Defaults to True (1)      |
        +-------------+----------------+-----------+---------------------------+

    Returns:     The newly created object hash.

    Example:
    # Create build by product ID and set the build active.
    >>> Build.create({'product': 234, 'name': 'tcms_testing', 'description': 'None', 'is_active': 1})
    # Create build by product name and set the build to inactive.
    >>> Build.create({'product': 'TCMS', 'name': 'tcms_testing 2', 'description': 'None', 'is_active': 0})
    """
    if not values.get('product') or not values.get('name'):
        raise ValueError('Product and name are both required.')

    p = pre_check_product(values)

    return TestBuild.objects.create(
        product = p,
        name = values['name'],
        description = values.get('description'),
        is_active = values.get('is_active', True)
    ).serialize()

def get(request, build_id):
    """
    Description: Used to load an existing build from the database.

    Params:      $id - An integer representing the ID in the database

    Returns:     A blessed Build object hash

    Example:
    >>> Build.get(1234)
    """
    return TestBuild.objects.get(build_id = build_id).serialize()

def get_runs(request, build_id):
    """
    Description: Returns the list of runs that this Build is used in.

    Params:      $id -  Integer: Build ID.

    Returns:     Array: List of run object hashes.

    Example:
    >>> Build.get_runs(1234)
    """
    from tcms.apps.testruns.models import TestRun

    tb = TestBuild.objects.get(build_id = build_id)
    query = {'build': tb}

    return TestRun.to_xmlrpc(query)

def get_caseruns(request, build_id):
    """
    Description: Returns the list of case-runs that this Build is used in.

    Params:      $id -  Integer: Build ID.

    Returns:     Array: List of case-run object hashes.

    Example:
    >>> Build.get_caseruns(1234)
    """
    from tcms.apps.testruns.models import TestCaseRun

    tb = TestBuild.objects.get(build_id = build_id)
    query = {'build': tb}

    return TestCaseRun.to_xmlrpc(query)

def lookup_id_by_name(request, name, product):
    """
    DEPRECATED - CONSIDERED HARMFUL Use Build.check_build instead
    """
    return check_build(request, name, product)

def lookup_name_by_id(request, build_id):
    """
    DEPRECATED Use Build.get instead
    """
    return get(request, build_id)

@log_call
@user_passes_test(lambda u: u.has_perm('management.change_testbuild'))
def update(request, build_id, values):
    """
    Description: Updates the fields of the selected build or builds.

    Params:      $id - Integer: A single build ID.

                 $values - Hash of keys matching Build fields and the new values
                 to set each field to.

        +-------------+----------------+-----------+---------------------------+
        | Field       | Type           | Null      | Description               |
        +-------------+----------------+-----------+---------------------------+
        | product     | Integer/String | Optional  | ID or Name of product     |
        | name        | String         | Optional  |                           |
        | description | String         | Optional  |                           |
        | is_active   | Boolean        | Optional  |                           |
        +-------------+----------------+-----------+---------------------------+

    Returns:     Hash: The updated Build object hash.

    Example:
    # Update name to 'foo' for build id 702
    >>> Build.update(702, {'name': 'foo'})
    # Update status to inactive for build id 702
    >>> Build.update(702, {'is_active': 0})
    """
    try:
        tb = TestBuild.objects.get(build_id = build_id)
    except TestBuild.DoesNotExist, error:
        return error

    try:
        if values.get('product'):
            p = check_product(values)
            tb.product = p

        if values.get('name'): tb.name = values['name']
        if values.get('description'): tb.description = values['description']
        if values.get('is_active'): tb.is_active = values.get('is_active', True)
        tb.save()
    except ValueError, error:
        return error
    except:
        return 'Unknown error'

    return tb.serialize()
