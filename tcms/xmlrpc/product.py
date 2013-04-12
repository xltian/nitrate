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

from kobo.django.xmlrpc.decorators import user_passes_test, login_required
from kobo.django.xmlrpc.decorators import log_call, log_traceback
from tcms.apps.management.models import Product
from utils import pre_check_product

__all__ = (
    'check_category',
    'check_component',
    'check_product',
    'filter',
    'filter_categories',
    'filter_components',
    'filter_versions',
    'get',
    'get_builds',
    'get_cases',
    'get_categories',
    'get_category',
    'get_component',
    'get_components',
    'get_environments',
    'get_milestones',
    'get_plans',
    'get_runs',
    'get_tag',
    'add_version',
    'get_versions',
    'lookup_name_by_id',
    'lookup_id_by_name',
)

def check_category(request, name, product):
    """
    Description: Looks up and returns a category by name.

    Params:      $name - String: name of the category.
                 $product - Integer/String
                            Integer: product_id of the product in the Database
                            String: Product name

    Returns:     Hash: Matching Category object hash or error if not found.

    Example:
    # Get with product ID
    >>> Product.check_category('Feature', 61)
    # Get with product name
    >>> Product.check_category('Feature', 'Red Hat Enterprise Linux 5')
    """
    from tcms.apps.testcases.models import TestCaseCategory
    p = pre_check_product(values = product)
    return TestCaseCategory.objects.get(name = name, product = p).serialize()

def check_component(request, name, product):
    """
    Description: Looks up and returns a component by name.

    Params:      $name - String: name of the category.
                 $product - Integer/String
                            Integer: product_id of the product in the Database
                            String: Product name

    Returns:     Hash: Matching component object hash or error if not found.

    Example:
    # Get with product ID
    >>> Product.check_component('acpi', 61)
    # Get with product name
    >>> Product.check_component('acpi', 'Red Hat Enterprise Linux 5')
    """
    from tcms.apps.management.models import Component
    p = pre_check_product(values = product)
    return Component.objects.get(name = name, product = p).serialize()

def check_product(request, name):
    """
    Description: Looks up and returns a validated product.

    Params:      $name - Integer/String
                         Integer: product_id of the product in the Database
                         String: Product name

    Returns:     Hash: Matching Product object hash or error if not found.

    Example:
    # Get with product ID
    >>> Product.check_product(61)
    # Get with product name
    >>> Product.check_product('Red Hat Enterprise Linux 5')
    """
    p = pre_check_product(values = name)
    return p.serialize()

def filter(request, query):
    """
    Description: Performs a search and returns the resulting list of products.

    Params:      $query - Hash: keys must match valid search fields.

    +------------------------------------------------------------------+
    |               Product Search Parameters                          |
    +------------------------------------------------------------------+
    |        Key          |          Valid Values                      |
    | id                  | Integer: ID of product                     |
    | name                | String                                     |
    | classification      | ForeignKey: Classfication                  |
    | description         | String                                     |
    +------------------------------------------------------------------+

    Returns:     Array: Matching products are retuned in a list of hashes.

    Example:
    # Get all of product named 'Red Hat Enterprise Linux 5'
    >>> Product.filter({'name': 'Red Hat Enterprise Linux 5'})
    """
    return Product.to_xmlrpc(query)

def filter_categories(request, query):
    """
    Description: Performs a search and returns the resulting list of categories.

    Params:      $query - Hash: keys must match valid search fields.

    +------------------------------------------------------------------+
    |              Component Search Parameters                         |
    +------------------------------------------------------------------+
    |        Key          |          Valid Values                      |
    | id                  | Integer: ID of product                     |
    | name                | String                                     |
    | product             | ForeignKey: Product                        |
    | description         | String                                     |
    +------------------------------------------------------------------+

    Returns:     Array: Matching categories are retuned in a list of hashes.

    Example:
    # Get all of categories named like 'libvirt'
    >>> Product.filter_categories({'name__icontains': 'regression'})
    # Get all of categories named in product 'Red Hat Enterprise Linux 5'
    >>> Product.filter_categories({'product__name': 'Red Hat Enterprise Linux 5'})
    """
    from tcms.apps.testcases.models import TestCaseCategory
    return TestCaseCategory.to_xmlrpc(query)

def filter_components(request, query):
    """
    Description: Performs a search and returns the resulting list of components.

    Params:      $query - Hash: keys must match valid search fields.

    +------------------------------------------------------------------+
    |              Component Search Parameters                         |
    +------------------------------------------------------------------+
    |        Key          |          Valid Values                      |
    | id                  | Integer: ID of product                     |
    | name                | String                                     |
    | product             | ForeignKey: Product                        |
    | initial_owner       | ForeignKey: Auth.User                      |
    | initial_qa_contact  | ForeignKey: Auth.User                      |
    | description         | String                                     |
    +------------------------------------------------------------------+

    Returns:     Array: Matching components are retuned in a list of hashes.

    Example:
    # Get all of components named like 'libvirt'
    >>> Product.filter_components({'name__icontains': 'libvirt'})
    # Get all of components named in product 'Red Hat Enterprise Linux 5'
    >>> Product.filter_components({'product__name': 'Red Hat Enterprise Linux 5'})
    """
    from tcms.apps.management.models import Component
    return Component.to_xmlrpc(query)

def filter_versions(request, query):
    """
    Description: Performs a search and returns the resulting list of versions.

    Params:      $query - Hash: keys must match valid search fields.

    +------------------------------------------------------------------+
    |              Component Search Parameters                         |
    +------------------------------------------------------------------+
    |        Key          |          Valid Values                      |
    | id                  | Integer: ID of product                     |
    | value               | String                                     |
    | product             | ForeignKey: Product                        |
    +------------------------------------------------------------------+

    Returns:     Array: Matching versions are retuned in a list of hashes.

    Example:
    # Get all of versions named like '2.4.0-SNAPSHOT'
    >>> Product.filter_versions({'value__icontains': '2.4.0-SNAPSHOT'})
    # Get all of filter_versions named in product 'Red Hat Enterprise Linux 5'
    >>> Product.filter_versions({'product__name': 'Red Hat Enterprise Linux 5'})
    """
    from tcms.apps.management.models import Version
    return Version.to_xmlrpc(query)

def get(request, id):
    """
    Description: Used to load an existing product from the database.

    Params:      $id - An integer representing the ID in the database

    Returns:     A blessed TCMS Product object hash

    Example:
    >>> Product.get(61)
    """
    return Product.objects.get(id = id).serialize()

def get_builds(request, product, is_active = True):
    """
    Description: Get the list of builds associated with this product.

    Params:      $product  -  Integer/String
                              Integer: product_id of the product in the Database
                              String: Product name
                 $is_active - Boolean: True to only include builds where is_active is true.
                              Default: True
    Returns:     Array: Returns an array of Build objects.

    Example:
    # Get with product id including all builds
    >>> Product.get_builds(61)
    # Get with product name excluding all inactive builds
    >>> Product.get_builds('Red Hat Enterprise Linux 5', 0)
    """
    from tcms.apps.management.models import TestBuild

    p = pre_check_product(values = product)
    query = {'product': p, 'is_active': is_active}
    return TestBuild.to_xmlrpc(query)

def get_cases(request, product):
    """
    Description: Get the list of cases associated with this product.

    Params:      $product - Integer/String
                            Integer: product_id of the product in the Database
                            String: Product name

    Returns:     Array: Returns an array of TestCase objects.

    Example:
    # Get with product id
    >>> Product.get_cases(61)
    # Get with product name
    >>> Product.get_cases('Red Hat Enterprise Linux 5')
    """
    from tcms.apps.testcases.models import TestCase
    p = pre_check_product(values = product)
    query = {'category__product': p}
    return TestCase.to_xmlrpc(query)

def get_categories(request, product):
    """
    Description: Get the list of categories associated with this product.

    Params:      $product - Integer/String
                            Integer: product_id of the product in the Database
                            String: Product name

    Returns:     Array: Returns an array of Case Category objects.

    Example:
    # Get with product id
    >>> Product.get_categories(61)
    # Get with product name
    >>> Product.get_categories('Red Hat Enterprise Linux 5')
    """
    from tcms.apps.testcases.models import TestCaseCategory
    p = pre_check_product(values = product)
    query = {'product': p}
    return TestCaseCategory.to_xmlrpc(query)

def get_category(request, id):
    """
    Description: Get the category matching the given id.

    Params:      $id - Integer: ID of the category in the database.

    Returns:     Hash: Category object hash.

    Example:
    >>> Product.get_category(11)
    """
    from tcms.apps.testcases.models import TestCaseCategory
    return TestCaseCategory.objects.get(id = id).serialize()

def get_component(request, id):
    """
    Description: Get the component matching the given id.

    Params:      $id - Integer: ID of the component in the database.

    Returns:     Hash: Component object hash.

    Example:
    >>> Product.get_component(11)
    """
    from tcms.apps.management.models import Component
    return Component.objects.get(id = id).serialize()

def get_components(request, product):
    """
    Description: Get the list of components associated with this product.

    Params:      $product - Integer/String
                            Integer: product_id of the product in the Database
                            String: Product name

    Returns:     Array: Returns an array of Component objects.

    Example:
    # Get with product id
    >>> Product.get_components(61)
    # Get with product name
    >>> Product.get_components('Red Hat Enterprise Linux 5')
    """
    from tcms.apps.management.models import Component
    p = pre_check_product(values = product)
    query = {'product': p}
    return Component.to_xmlrpc(query)

def get_environments(request, product):
    """FIXME: NOT IMPLEMENTED"""
    pass

def get_milestones(request, product):
    """FIXME: NOT IMPLEMENTED"""
    pass

def get_plans(request, product):
    """
    Description: Get the list of plans associated with this product.

    Params:      $product - Integer/String
                            Integer: product_id of the product in the Database
                            String: Product name

    Returns:     Array: Returns an array of Test Plan objects.

    Example:
    # Get with product id
    >>> Product.get_plans(61)
    # Get with product name
    >>> Product.get_plans('Red Hat Enterprise Linux 5')
    """
    from tcms.apps.testplans.models import TestPlan
    p = pre_check_product(values = product)
    query = {'product': p}
    return TestPlan.to_xmlrpc(query)

def get_runs(request, product):
    """
    Description: Get the list of runs associated with this product.

    Params:      $product - Integer/String
                            Integer: product_id of the product in the Database
                            String: Product name

    Returns:     Array: Returns an array of Test Run objects.

    Example:
    # Get with product id
    >>> Product.get_runs(61)
    # Get with product name
    >>> Product.get_runs('Red Hat Enterprise Linux 5')
    """
    from tcms.apps.testruns.models import TestRun
    p = pre_check_product(values = product)
    query = {'build__product': p}
    return TestRun.to_xmlrpc(query)

def get_tag(request, id):
    """
    Description: Get the list of tags.

    Params:      $id   - Integer: ID of the tag in the database.

    Returns:     Array: Returns an array of Tags objects.

    Example:
    >>> Product.get_tag(10)
    """
    from tcms.apps.management.models import TestTag
    return TestTag.objects.get(pk=id).serialize()

@log_call
@user_passes_test(lambda u: u.has_perm('management.add_version'))
def add_version(request, values):
    """
    Description: Add version to specified product.

    Params:      $product - Integer/String
                            Integer: product_id of the product in the Database
                            String: Product name
                 $value   - String
                            The name of the version string.

    Returns:     Array: Returns the newly added version object, error info if failed.

    Example:
    # Add version for specified product:
    >>> Product.add_version({'value': 'devel', 'product': 272})
    {'product': 'QE Test Product', 'id': '1106', 'value': 'devel', 'product_id': 272}
    # Run it again:
    >>> Product.add_version({'value': 'devel', 'product': 272})
    [['__all__', 'Version with this Product and Value already exists.']]
    """
    from tcms.apps.management.forms import VersionForm
    from tcms.core import forms

    form = VersionForm(values)
    if form.is_valid():
        version = form.save()
        return version.serialize()

    else:
        return forms.errors_to_list(form)


def get_versions(request, product):
    """
    Description: Get the list of versions associated with this product.

    Params:      $product - Integer/String
                            Integer: product_id of the product in the Database
                            String: Product name

    Returns:     Array: Returns an array of Version objects.

    Example:
    # Get with product id
    >>> Product.get_runs(61)
    # Get with product name
    >>> Product.get_runs('Red Hat Enterprise Linux 5')
    """
    from tcms.apps.management.models import Version
    p = pre_check_product(values = product)
    query = {'product': p}
    return Version.to_xmlrpc(query)

def lookup_name_by_id(request, id):
    """DEPRECATED Use Product.get instead"""
    return get(request, id)

def lookup_id_by_name(request, name):
    """DEPRECATED - CONSIDERED HARMFUL Use Product.check_product instead"""
    return check_product(request, name)
