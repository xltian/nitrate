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
#   Chaobin Tang <ctang@redhat.com>

'''
Generate a brief testcaserun report on product version
'''

import csv
from tcms.apps.management.models import Product, Version
from tcms.apps.testruns.models import TestCaseRun


def get_products_by_name(name):
    try:
        product = Product.objects.get(name=name)
    except Product.DoesNotExist:
        product = None
    return product

def report(name):
    product = get_products_by_name(name)
    if product is None:
        return None
    all_versions = product.version.all()
    reports = []
    for version in all_versions:
        caseruns = TestCaseRun.objects.filter(
            run__build__product=product,
            run__product_version=version.value
        )
        automated_caseruns = caseruns.filter(case__is_automated=True)
        non_automated_caseruns = caseruns.filter(case__is_automated=False)
        both = caseruns.filter(case__is_automated=2)
        metric = {
            'automated': automated_caseruns.count(),
            'manual': non_automated_caseruns.count(),
            'both': both.count()
        }
        reports.append((version.value, metric))
    return reports

def all_rhel():
    reports = []
    base_name = 'Red Hat Enterprise Linux %s'
    for i in (4, 5, 6):
        prod_name = (base_name % i)
        result = (prod_name, report(prod_name))
        reports.append(result)
    return reports

def output(reports):
    file_name = 'caserun_reports.csv'
    writer = csv.writer(open(file_name, 'w'))
    header = ('Product', 'Manual CaseRuns', 'Automated CaseRuns', 'Both')
    writer.writerow(header)
    for product, versions in reports:
        for version, report in versions:
            product_name_with_version = (
                '%s - %s' % (product, version)
            )
            line = (
                product_name_with_version,
                report['manual'],
                report['automated'],
                report['both']
            )
            writer.writerow(line)
