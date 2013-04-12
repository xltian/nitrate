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

'''
Advance search implementations
'''

# from django
from django.http import HttpRequest, HttpResponse, Http404
from django import template
from django.shortcuts import render_to_response
from django.views.generic.simple import direct_to_template
from django.conf import settings
from django.core.cache import cache
from django.db.models.query import QuerySet

# from tcms
from tcms.apps.testplans.models import TestPlan, TestPlanType
from tcms.apps.testcases.models import TestCase
from tcms.apps.testruns.models import TestRun
from tcms.apps.management.models import Product, Version, Priority
from tcms.search.query import SmartDjangoQuery
from tcms.search.forms import CaseForm, RunForm, PlanForm
from tcms.search.order import order_targets
from tcms.core.helpers.cache import cached_entities
from tcms.core.utils.raw_sql import RawSQL

# from stdlib
from datetime import datetime
import time

def advance_search(request, tmpl='search/advanced_search.html'):
    '''
    View of /advance-search/
    '''
    errors      = None
    data        = request.GET
    target      = data.get('target')
    plan_form   = PlanForm(data)
    case_form   = CaseForm(data)
    run_form    = RunForm(data)
    # Update MultipleModelChoiceField on each form dynamically
    plan_form.populate(data)
    case_form.populate(data)
    run_form.populate(data)
    all_forms   = (plan_form, case_form, run_form)
    errors      = [f.errors for f in all_forms if not f.is_valid()]
    if errors or not data:
        PRODUCT_CHOICE = [
            (p.pk, p.name) for p in cached_entities('product')
        ]
        PLAN_TYPE_CHOICES = cached_entities('testplantype')
        errors = fmt_errors(errors)
        return direct_to_template(request, tmpl, locals())

    start = time.time()
    results = query(request, plan_form.cleaned_data,
        run_form.cleaned_data, case_form.cleaned_data, target)
    results = order_targets(target, results, data)
    end = time.time()
    timecost = round(end - start, 3)
    queries = fmt_queries(*[f.cleaned_data for f in all_forms])
    queries['Target'] = target
    return render_results(request, results, timecost, queries)

def query(request, plan_query, run_query, case_query, target, using='orm'):
    USING = {
        'orm': {
            'query': SmartDjangoQuery,
            'sum': sum_orm_queries
        }
    }
    Query   = USING[using]['query']
    Sum     = USING[using]['sum']
    plans   = Query(plan_query, TestPlan.__name__)
    runs    = Query(run_query, TestRun.__name__)
    cases   = Query(case_query, TestCase.__name__)
    results = Sum(plans, cases, runs, target)
    return results

def sum_orm_queries(plans, cases, runs, target):
    plans = plans.evaluate()
    cases = cases.evaluate()
    runs  = runs.evaluate()
    if target == 'run':
        if not plans and not cases:
            if runs is None:
                runs = TestRun.objects.none()
        if runs is None:
            runs = TestRun.objects.all()
        if cases:
            runs = runs.filter(case_run__case__in=cases).distinct()
        if plans:
            runs = runs.filter(plan__in=plans).distinct()
        runs = runs.extra(
            select={
                'env_groups': RawSQL.environment_group_for_run,
            }
        )
        return runs
    if target == 'plan':
        if not cases and not runs:
            if plans is None:
                plans = TestPlan.objects.none()
        if plans is None:
            plans = TestPlan.objects.all()
        if cases:
            plans = plans.filter(case__in=cases).distinct()
        if runs:
            plans = plans.filter(run__in=runs).distinct()
        plans = plans.extra(select = {
                'num_cases': RawSQL.num_cases,
                'num_runs': RawSQL.num_runs,
                'num_children': RawSQL.num_plans,
            })
        return plans
    if target == 'case':
        if not plans and not runs:
            if cases is None:
                cases = TestCase.objects.none()
        if cases is None:
            cases = TestCase.objects.all()
        if runs:
            cases = cases.filter(case_run__run__in=runs).distinct()
        if plans:
            cases = cases.filter(plan__in=plans).distinct()
        return cases

def render_results(request, results, time_cost, queries, tmpl='search/results.html'):
    '''
    Using a SQL "in" query and PKs as the arguments.
    '''
    klasses = {
        'plan': {'class': TestPlan, 'result_key': 'test_plans'},
        'case': {'class': TestCase, 'result_key': 'test_cases'},
        'run': {'class': TestRun, 'result_key': 'test_runs'}
    }
    asc = bool(request.REQUEST.get('asc', None))
    query_url = remove_from_request_path(request, 'order_by')
    if asc:
        query_url = remove_from_request_path(query_url, 'asc')
    else:
        query_url = '%s&asc=True' % query_url
    return direct_to_template(request, tmpl,
        {
            klasses[request.GET['target']]['result_key']: results,
            'time_cost': time_cost,
            'queries': queries,
            'query_url': query_url,
        }
    )

def remove_from_request_path(request, name):
    '''
    Remove a parameter from request.get_full_path()\n
    and return the modified path afterwards.
    '''
    if isinstance(request, HttpRequest):
        path = request.get_full_path()
    else:
        path = request
    path = path.split('?')
    if len(path) > 1:
        path = path[1].split('&')
    else:
        return None
    path = [p for p in path if not p.startswith(name)]
    path = '&'.join(path)
    return '?' + path

def fmt_errors(form_errors):
    '''
    Format errors collected in a Django Form
    for a better appearance.
    '''
    errors = []
    for error in form_errors:
        for k, v in error.iteritems():
            k = k.replace('p_product', 'product').replace('p_', 'product ').replace('cs_', 'case ')\
            .replace('pl_', 'plan ').replace('r_', 'run ').replace('_', ' ')
            if isinstance(v, list):
                v = ', '.join(map(str, v))
            errors.append((k, v))
    return errors

def fmt_queries(*queries):
    '''
    Format the queries string.
    '''
    results = {}
    for query in queries:
        for k, v in query.iteritems():
            k = k.replace('p_product', 'product').replace('p_', 'product ').replace('cs_', 'case ')\
            .replace('pl_', 'plan ').replace('r_', 'run ').replace('_', ' ')
            if isinstance(v, bool) or v:
                if isinstance(v, QuerySet):
                    try:
                        v = ', '.join([o.name for o in v])
                    except AttributeError:
                        try:
                            v = ', '.join([o.value for o in v])
                        except AttributeError:
                            v = ', '.join(v)
                if isinstance(v, list):
                    v = ', '.join(map(str, v))
                results[k] = v
    return results

if __name__ == '__main__':
    import doctest
    doctest.testmod()
