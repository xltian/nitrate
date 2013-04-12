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
#   Xuqing Kuang <xkuang@redhat.com> Chaobin Tang <ctang@redhat.com>

'''
Warning. Before you attempt to do anything
in here, it is well suggested that you read
PRD 3.4.1 for a reference.
'''


from tcms.search.forms import RunForm
from tcms.search.query import SmartDjangoQuery
from tcms.apps.testruns.models import TestRun, TestCaseRun
from tcms.apps.testruns.models import TestCaseRunStatus
from tcms.core.utils.raw_sql import ReportSQL
from tcms.apps.testplans.models import TestPlan

from itertools import groupby

def annotate_runs_with_case_run_count_by_status(runs):
    '''
    Working with a testrun queryset.\n
    Annotate it with case count of different status\n
    so that each run in the queryset comes\n
    with statistics of case of different status.\n
    Implementation using queryset.extra and\n
    hand-written SQL.
    '''
    run_statuses  = TestCaseRunStatus.objects.all()
    _sql = ReportSQL.case_runs_count_by_status_under_run
    _select = {}
    for status in run_statuses:
        key     = status.name.lower() + '_count'
        value   = _sql % status.pk
        _select[key] = value
    return runs.extra(select=_select)

def get_caserun_percentages(caseruns):
    '''
    calculate percentages of caseruns in defferent status.
    '''
    percentages = {}
    for caserun in caseruns:
        status = caserun.case_run_status.name.lower()
        count = percentages.setdefault(status, 0)
        percentages[status] = count + 1
    return percentages

def search_runs(queries):
    runs    = SmartDjangoQuery(queries, TestRun.__name__)
    runs    = runs.evaluate()
    if runs is None:
        return None
    #runs    = annotate_runs_with_case_run_count_by_status(runs)
    return runs

def group_test_run(runs, key):
    grouped_runs = []
    if not runs:
        return []
    _key_func = lambda r: getattr(r, key)
    return grouped_runs

def test_run_report(queries, report_type):
    runs    = search_runs(queries)
    data    = {}
    reports = []
    builds  = queries.get('r_build')
    data['runs_count'] = runs.count()
    data['plans_count'] = TestPlan.objects.filter(run__in=runs).distinct().count()
    data['caseruns_count'] = TestCaseRun.objects.filter(run__in=runs).distinct().count()
    reports = get_reports(runs, report_type, bool(builds))
    data['reports'] = reports
    builds_selected = bool(builds)
    data['builds_selected'] = builds_selected
    if not builds_selected:
        builds = set(r.build.name for r in runs)
        data['builds'] = builds
    return data

def get_reports(runs, report_type, group_by_builds=False):
    report = []
    if report_type == 'per_build_report':
        if group_by_builds:
            report = test_run_report_by_build(runs, test_run_report_by_tester_with_percentages)
        else:
            report = test_run_report_by_tester_with_percentages(runs)
    if report_type == 'per_priority_report':
        report = test_run_report_by_case_priority(runs)
    if report_type == 'per_plan_tag_report':
        report = test_run_report_by_plan_tag(runs)
    if report_type == 'per_plan_build_report':
        report = test_run_report_by_plan_build(runs)
    if report_type == 'runs_with_rates_per_plan_tag':
        report = percentages_on_runs_under_plan_tag(runs)
    if report_type == 'runs_with_rates_per_plan_build':
        report = percentages_on_runs_under_plan_build(runs)
    return report

def test_run_report_by_build(runs, inner_group=None):
    report = []
    if hasattr(runs, 'order_by'):
        runs = runs.order_by('build')
    else:
        runs = sorted(runs, key=lambda r: r.build_id)
    runs    = groupby(runs, lambda r: r.build)
    for build, _runs in runs:
        __runs = _runs
        if inner_group:
            __runs = inner_group(_runs)
        report.append((build, list(__runs)))
    return report

def get_caseruns_from_runs(runs):
    #caseruns    = (csr for run in runs for csr in run.case_run.all())
    caseruns    = TestCaseRun.objects.filter(run__in=runs)
    return caseruns

def test_run_report_by_tester_with_percentages(runs, inner_group=None):
    report = []
    caseruns    = get_caseruns_from_runs(runs)
    caseruns    = group_caserun_by_tester(caseruns)
    for tester, _caseruns in caseruns:
        __caseruns = list(_caseruns)
        summed_runs = set(c.run for c in __caseruns)
        percentages = get_caserun_percentages(__caseruns)
        if inner_group:
            __caseruns = inner_group(__caseruns)
        report.append((tester, summed_runs, __caseruns, percentages))
    return report

def test_run_report_by_case_priority(runs):
    report    = test_run_report_by_build(runs, test_run_report_by_priority_with_percentages)
    return report

def test_run_report_by_plan_tag(runs):
    runs    = annotate_runs_with_case_run_count_by_status(runs)
    runs_grouped_by_plan_tag = group_runs_by_plan_tag(runs)
    report = []
    for tag, _runs in runs_grouped_by_plan_tag.iteritems():
        runs_grouped_by_build = test_run_report_by_build(_runs)
        plans_count = len(set(r.plan_id for r in _runs))
        caserun_count = TestCaseRun.objects.filter(run__in=_runs).count()
        report.append((tag, len(_runs), plans_count, caserun_count, runs_grouped_by_build))
    return report

def test_run_report_by_plan_build(runs):
    runs    = annotate_runs_with_case_run_count_by_status(runs)
    runs_grouped_by_plan = group_runs_by_plan(runs)
    report = []
    for plan, _runs in runs_grouped_by_plan.iteritems():
        runs_grouped_by_build = test_run_report_by_build(_runs)
        plans_count = len(set(r.plan_id for r in _runs))
        caserun_count = TestCaseRun.objects.filter(run__in=_runs).count()
        report.append((plan, len(_runs), plans_count, caserun_count, runs_grouped_by_build))
    return report

def group_caserun_by_tester(caseruns):
    caseruns    = sorted(caseruns, key=lambda csr: csr.tested_by_id)
    caseruns    = groupby(caseruns, key=lambda csr: csr.tested_by)
    return caseruns

def test_run_report_by_priority_with_percentages(runs):
    report = []
    caseruns    = get_caseruns_from_runs(runs)
    caseruns    = sorted(caseruns, key=lambda c: c.case.priority_id)
    caseruns    = groupby(caseruns, key=lambda c: c.case.priority)
    for priority, _caseruns in caseruns:
        __caseruns = list(_caseruns)
        percentages = get_caserun_percentages(__caseruns)
        report.append((priority, percentages, len(__caseruns)))
    return report

def percentages_on_runs_under_plan_tag(runs):
    report = []
    grouped_runs_by_plan = group_runs_by_plan_tag(runs)
    for plan_tag, _runs in grouped_runs_by_plan.iteritems():
        plans_count = len(set(r.plan_id for r in _runs))
        runs_count = len(_runs)
        passed, failed = get_runs_rate(_runs)
        report.append((plan_tag, plans_count, runs_count, passed, failed))
    return report

def percentages_on_runs_under_plan_build(runs):
    report = []
    grouped_runs_by_plan = group_runs_by_plan(runs)
    for plan, _runs in grouped_runs_by_plan.iteritems():
        runs_count = len(_runs)
        builds_count = len(set(r.build_id for r in _runs))
        passed, failed = get_runs_rate(_runs)
        report.append((plan, builds_count, runs_count, passed, failed))
    return report

def get_runs_rate(runs):
    '''
    Two counts:
    1. runs with all caserun passed
    2. runs with all caserun failed
    '''
    total_count = float(len(runs))
    passed_count = 0
    failed_count = 0
    PASSED = 2
    FAILED = 3
    for run in runs:
        statuses = run.case_run.values_list('case_run_status_id', flat=True)
        if member_purified(statuses, lambda i: i==PASSED):
            passed_count += 1
        if member_purified(statuses, lambda i: i==FAILED):
            failed_count += 1
    return passed_count, failed_count

def member_purified(iterable, condition):
    '''
    Testing each member in the iterable
    with condition. Return boolean indicating
    a perfection indicating all members purified.
    '''
    perfection = True
    for elem in iterable:
        if not condition(elem):
            perfection = False
            break
    return perfection

def group_runs_by_plan_tag(runs):
    tag_run_map = {'untagged': []}
    un_tagged_runs = tag_run_map['untagged']
    for run in runs:
        run_tags = run.plan.tag.values_list('name', flat=True)
        if not run_tags:
            un_tagged_runs.append(run)
            continue
        map(lambda t: tag_run_map.setdefault(t, []).append(run), run_tags)
    return tag_run_map

def group_runs_by_plan(runs):
    plan_run_map = {}
    for run in runs:
        (lambda t: plan_run_map.setdefault(t, []).append(run))(run.plan)
    return plan_run_map

if __name__ == '__main__':
    import doctest
    doctest.testmod()
