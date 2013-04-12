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
#   Xuqing Kuang <xkuang@redhat.com>, Chaobin Tang <ctang@redhat.com>

def order_targets(target, queryset, queries):
    '''
    Designed to work with advance search module.
    Ordering queryset of testplan, testcase, or testrun.
    @ target: string, 'plan','run', 'case'
    @ queryset: django queryset
    @ queries: form.cleaned_data
    '''
    order_options = {
        'plan': {
            'default_order_by': 'create_date',
            'orderer': order_plan_queryset,
        },
        'run': {
            'default_order_by': 'create_date',
            'orderer': order_run_queryset,
        },
        'case': {
            'default_order_by': 'create_date',
            'orderer': order_case_queryset,
        },
    }
    orderer = order_options[target]['orderer']
    default_order_by = order_options[target]['default_order_by']
    order_by = queries.get('order_by', default_order_by)
    asc = bool(queries.get('asc', None))
    ordered_set = orderer(queryset, order_by, asc)
    return ordered_set

def order_plan_queryset(plans, field, asc=False):
    '''
    Annotate the TestPlan queryset
    by calling order_by on it.
    '''
    orderable_fields = (
        'plan_id', 'name', 'author__username', 'owner__username',
        'create_date', 'product__name', 'type',
        'num_cases', 'num_runs', 'num_children',
    )
    if field in orderable_fields:
        order_by = field
        if not asc:
            order_by = '-%s' % order_by
        plans = plans.order_by(order_by)
    return plans

def order_run_queryset(runs, field, asc=False):
    '''
    Annotate the TestRun queryset
    by calling order_by on it.
    '''
    orderable_fields = (
        'run_id', 'summary', 'manager__username',
        'default_tester__username', 'env_groups',
        'build__product__name', 'product_version',
        'plan__name'
    )
    if field in orderable_fields:
        order_by = field
        if not asc:
            order_by = '-%s' % order_by
        runs = runs.order_by(order_by)
    return runs

def order_case_queryset(cases, field, asc=False):
    '''
    Annotate the TestCase queryset
    by calling order_by on it.
    '''
    orderable_fields = (
        'case_id', 'summary', 'author__username', 
        'default_tester__username', 'priority',
        'is_automated', 'category__name', 'case_status',
        'create_date'
    )
    if field in orderable_fields:
        order_by = field
        if not asc:
            order_by = '-%s' % order_by
        cases = cases.order_by(order_by)
    return cases
