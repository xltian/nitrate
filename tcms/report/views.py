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

from django.db import connection, transaction
from django.views.generic.simple import direct_to_template
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from tcms.apps.testruns.models import TestRun, TestCaseRun
from tcms.apps.management.models import Classification, Product, Component
from tcms.core.utils import calc_percent
from tcms.core.utils.counter import CaseRunStatusCounter, RunsCounter
from tcms.core.utils.raw_sql import ReportSQL as RawSQL
from tcms.core.helpers.cache import cached_entities
from tcms.search.forms import RunForm
from tcms.report.targets.run import search_runs, test_run_report
from tcms.search import fmt_queries, remove_from_request_path

MODULE_NAME = "report"

def overall(request, template_name='report/list.html'):
    """Overall of products report"""
    SUB_MODULE_NAME = 'overall'
    products = Product.objects.all()

    products = products.extra(select={
        'plans_count': RawSQL.index_product_plans_count,
        'runs_count': RawSQL.index_product_runs_count,
        'cases_count': RawSQL.index_product_cases_count,
    })

    return direct_to_template(request, template_name, {
        'module': MODULE_NAME,
        'sub_module': SUB_MODULE_NAME,
        'products': products
    })

def overview(request, product_id, template_name='report/overview.html'):
    """Product for a product"""
    SUB_MODULE_NAME = 'overview'

    try:
        product = Product.objects.get(id = product_id)
    except Product.DoesNotExist, error:
        raise Http404(error)

    cursor = connection.cursor()
    cursor.execute(RawSQL.overview_runing_runs_count, [product.id])
    rows = cursor.fetchall()

    if len(rows) == 2:
        runs_count = RunsCounter(rows[0][1], rows[1][1])
    else:
        runs_count = RunsCounter()

        for row in rows:
            setattr(runs_count, row[0], row[1])

    cursor.execute(RawSQL.overview_case_runs_count, [product.id])
    rows = cursor.fetchall()

    total = 0
    for row in rows:
        if row[0]:
            total += row[1]

    trs = TestRun.objects.filter(plan__product = product)
    tcrs = TestCaseRun.objects.filter(run__in = trs)
    case_run_counter = CaseRunStatusCounter(tcrs)
    for row in rows:
        if row[0]:
            setattr(case_run_counter, row[0], row[1])
            setattr(case_run_counter, row[0] + '_percent', float(row[1]) / total * 100)

    return direct_to_template(request, template_name, {
        'module': MODULE_NAME,
        'sub_module': SUB_MODULE_NAME,
        'product': product,
        'runs_count': runs_count,
        'case_run_count': case_run_counter,
    })

def version(request, product_id, template_name='report/version.html'):
    """Version report for a product"""
    SUB_MODULE_NAME = 'version'

    try:
        product = Product.objects.get(id = product_id)
    except ObjectDoesNotExist, error:
        raise Http404(error)

    versions = product.version.all()
    versions = versions.extra(select={
        'plans_count': RawSQL.version_plans_count,
        'running_runs_count': RawSQL.version_running_runs_count,
        'finished_runs_count': RawSQL.version_finished_runs_count,
        'cases_count': RawSQL.version_cases_count,
        'case_run_percent': RawSQL.version_case_run_percent,
        'failed_case_runs_count': RawSQL.version_failed_case_runs_count,
    })

    case_run_counter = None
    current_version = None
    if request.REQUEST.get('version_id'):
        try:
            current_version = product.version.get(id = request.REQUEST['version_id'])
        except ObjectDoesNotExist, error:
            raise Http404(error)

        cursor = connection.cursor()
        cursor.execute(RawSQL.version_case_runs_count, [
            product.id,
            current_version.value,
        ])
        rows = cursor.fetchall()
        total = 0
        for row in rows:
            if row[0]:
                total += row[1]

        case_run_counter = CaseRunStatusCounter([])
        for row in rows:
            if row[0]:
                setattr(case_run_counter, row[0], row[1])
                setattr(case_run_counter, row[0] + '_percent', float(row[1]) / total * 100)

    return direct_to_template(request, template_name, {
        'module': MODULE_NAME,
        'sub_module': SUB_MODULE_NAME,
        'product': product,
        'versions': versions,
        'version': current_version,
        'case_run_count': case_run_counter,
    })

def build(request, product_id, template_name='report/build.html'):
    """Build report for a product"""
    SUB_MODULE_NAME = 'build'

    try:
        product = Product.objects.get(id = product_id)
    except ObjectDoesNotExist, error:
        raise Http404(error)

    builds = product.build.all()
    builds = builds.extra(select={
        'total_runs': RawSQL.build_total_runs,
        'finished_runs': RawSQL.build_finished_runs,
        'finished_case_run_percent': RawSQL.build_finished_case_runs_percent,
        'failed_case_run_count': RawSQL.build_failed_case_run_count,
    })

    case_run_counter = None
    current_build = None
    if request.REQUEST.get('build_id'):
        try:
            current_build = product.build.get(build_id = request.REQUEST['build_id'])
        except ObjectDoesNotExist, error:
            raise Http404(error)

        cursor = connection.cursor()
        cursor.execute(RawSQL.build_case_runs_count, [current_build.build_id, ])
        rows = cursor.fetchall()
        total = 0
        for row in rows:
            if row[0]:
                total += row[1]
        trs = current_build.testcaserun_set.all()
        case_run_counter = CaseRunStatusCounter(trs)
        for row in rows:
            if row[0]:
                setattr(case_run_counter, row[0], row[1])
                setattr(case_run_counter, row[0] + '_percent', float(row[1]) / total * 100)

    return direct_to_template(request, template_name, {
        'module': MODULE_NAME,
        'sub_module': SUB_MODULE_NAME,
        'product': product,
        'builds': builds,
        'build': current_build,
        'case_run_count': case_run_counter
    })

def component(request, product_id, template_name='report/component.html'):
    """Component report for a product"""
    SUB_MODULE_NAME = 'component'

    try:
        product = Product.objects.get(id = product_id)
    except Product.DoesNotExist, error:
        raise Http404(error)

    components = product.component.all()
    components = components.extra(select={
        'total_cases': RawSQL.component_total_cases,
        'finished_case_run_percent': RawSQL.component_finished_case_run_percent,
        'failed_case_run_count': RawSQL.component_failed_case_run_count,
    })

    case_run_counter = None
    current_component = None
    if request.REQUEST.get('component_id'):
        try:
            current_component = product.component.get(id = request.REQUEST['component_id'])
        except ObjectDoesNotExist, error:
            raise Http404(error)

        cursor = connection.cursor()
        cursor.execute(RawSQL.component_case_runs_count, [current_component.id, ])
        rows = cursor.fetchall()
        total = 0
        for row in rows:
            if row[0]:
                total += row[1]

        component = Component.objects.get(id=request.GET.get('component_id'))
        tcs = component.testcase_set.all()
        tcrs = TestCaseRun.objects.filter(case__in=tcs)
        case_run_counter = CaseRunStatusCounter(tcrs)
        for row in rows:
            if row[0]:
                setattr(case_run_counter, row[0], row[1])
                setattr(case_run_counter, row[0] + '_percent', float(row[1]) / total * 100)

    return direct_to_template(request, template_name, {
        'module': MODULE_NAME,
        'sub_module': SUB_MODULE_NAME,
        'product': product,
        'components': components,
        'component': current_component,
        'case_run_count': case_run_counter
    })

def custom_search(request, template_name='report/custom_search.html'):
    """Custom report with search function"""
    from tcms.apps.management.models import TestBuild
    from tcms.apps.testruns.models import TestCaseRunStatus
    from forms import CustomSearchForm

    SUB_MODULE_NAME = 'custom_search'
    total_plans_count = 0
    total_runs_count = 0
    auto_count = manual_count = both_count = total_count = 0
    default_case_run_status = TestCaseRunStatus.objects.filter(name__in = ['passed', 'failed'])

    if request.REQUEST.get('a', '').lower() == 'search':
        form = CustomSearchForm(request.REQUEST)
        form.populate(product_id = request.REQUEST.get('product'))
        if form.is_valid():
            tbs = TestBuild.objects
            for k, v in form.fields.items():
                if form.cleaned_data[k]:
                    tbs = tbs.filter(**{k: form.cleaned_data[k]})

            extra_query = {
                'plans_count': RawSQL.custom_search_plans_count,
                'runs_count': RawSQL.custom_search_runs_count,
                'case_runs_count': RawSQL.custom_search_case_runs_count_under_run,
            }
            for tcrss in default_case_run_status:
                extra_query['case_runs_' + tcrss.name.lower() + '_count'] = RawSQL.custom_search_case_runs_count_by_status_under_run % tcrss.pk


            tbs = tbs.distinct()
            tbs = tbs.extra(select=extra_query)

            total_plans_count = sum(filter(lambda s: s is not None, tbs.values_list('plans_count', flat = True)))
            total_runs_count = sum(filter(lambda s: s is not None, tbs.values_list('runs_count', flat = True)))
            trs = TestRun.objects.select_related('build', 'case_run')
            trs = TestRun.objects.filter(build__in = tbs)
            for tr in trs:
                manual_count += tr.case_run.get_manual_case_count()
                auto_count += tr.case_run.get_automated_case_count()
                both_count += tr.case_run.get_both()

        else:
            tbs = TestBuild.objects.none()
    else:
        form = CustomSearchForm()
        tbs = TestBuild.objects.none()

    for tcrss in default_case_run_status:
        for tb in tbs:
            setattr(tb, 'case_runs_%s_percent' % tcrss.name.lower(), calc_percent(getattr(tb, 'case_runs_%s_count' % tcrss.name.lower()), tb.case_runs_count))

    return direct_to_template(request, template_name, {
        'module': MODULE_NAME,
        'sub_module': SUB_MODULE_NAME,
        'form': form,
        'builds': tbs,
        'total_plans_count': total_plans_count,
        'total_runs_count': total_runs_count,
        'manual_count': manual_count,
        'auto_count': auto_count,
        'both_count': both_count,
        'total_count': manual_count + auto_count + both_count,
    })

def custom_details(request, template_name='report/custom_details.html'):
    """Custom report with search function"""
    from tcms.apps.management.models import TestBuild
    from tcms.apps.testplans.models import TestPlan
    from tcms.apps.testruns.models import TestCaseRun, TestCaseRunStatus, TestRun
    from forms import CustomSearchDetailsForm
    SUB_MODULE_NAME = 'custom_search'

    default_case_run_status = TestCaseRunStatus.objects.all()
    auto_count = manual_count = both_count = total_count = 0
    tbs = tps = trs = tcrs = tcrses = None

    form = CustomSearchDetailsForm(request.REQUEST)
    form.populate(product_id = request.REQUEST.get('product'))
    if form.is_valid():
        tcrses = TestCaseRunStatus.objects.all()

        tbs = TestBuild.objects.filter(pk__in = request.REQUEST.getlist('pk__in'))
        tps = TestPlan.objects.filter(run__build__in = tbs)
        trs = TestRun.objects.filter(build__in = tbs)
        tcrs = TestCaseRun.objects.select_related('case', 'run', 'case_run_status', 'tested_by')
        tcrs = tcrs.filter(run__build__in = tbs)

#        if form.cleaned_data['product']:
#            tps = tps.filter(run__build__product = form.cleaned_data['product'])
#            trs = trs.filter(build__product = form.cleaned_data['product'])
#            tcrs = tcrs.filter(run__build__product = form.cleaned_data['product'])
#
#        if form.cleaned_data['build_run__product_version']:
#            tps = tps.filter(run__product_version = form.cleaned_data['build_run__product_version'])
#            trs = trs.filter(product_version = form.cleaned_data['build_run__product_version'])
#            tcrs = tcrs.filter(run__product_version = form.cleaned_data['build_run__product_version'])

        extra_query = {
            'plans_count': RawSQL.custom_search_plans_count,
            'runs_count': RawSQL.custom_search_runs_count,
            'case_runs_count': RawSQL.custom_search_case_runs_count_under_run,
        }
        for tcrss in default_case_run_status:
            extra_query['case_runs_' + tcrss.name.lower() + '_count'] = RawSQL.custom_search_case_runs_count_by_status_under_run % tcrss.pk

        tbs = tbs.distinct()
        tbs = tbs.extra(select=extra_query)
        tps = tps.distinct()
        trs = trs.filter(plan__in = tps).distinct()

        for tp in tps:
            tp.runs = []

            for tr in trs:
                if tp.plan_id == tr.plan_id:
                    tp.runs.append(tr)

        tcrs = tcrs.distinct()
        Manual = 0
        Automated = 1
        Both = 2
        both_count = tcrs.filter(case__is_automated = Both).count()
        auto_count = tcrs.filter(case__is_automated = Automated).count()
        manual_count = tcrs.filter(case__is_automated = Manual).count()
        total_count = both_count + auto_count + manual_count

        cursor = connection.cursor()
        for tr in trs:
            cursor.execute(RawSQL.custom_details_case_run_count % tr.pk)
            for s, n in cursor.fetchall():
                setattr(tr, s, n)

        for tcrss in default_case_run_status:
            for tb in tbs:
                setattr(tb, 'case_runs_%s_percent' % tcrss.name.lower(), calc_percent(getattr(tb, 'case_runs_%s_count' % tcrss.name.lower()), tb.case_runs_count))

    return direct_to_template(request, template_name, {
        'module': MODULE_NAME,
        'sub_module': SUB_MODULE_NAME,
        'form': form,
        'builds': tbs,
        'test_plans': tps,
        'test_runs': trs,
        'test_case_runs': tcrs,
        'test_case_run_status': tcrses,
        'total_count': total_count,
        'manual_count': manual_count,
        'auto_count': auto_count,
        'both_count': both_count,
    })

def view_test_run_report(request):
    templates = {
        'per_build_report': 'report/caserun_report_per_build.html',
        'per_tester_report': 'report/caserun_report_per_tester.html',
        'per_priority_report': 'report/caserun_report_per_priority.html',
        'per_plan_tag_report': 'report/testrun_report_per_plan_tag.html',
        'per_plan_build_report': 'report/testrun_report_per_plan_build.html',
        'runs_with_rates_per_plan_tag': 'report/testrun_report_by_plan_tag_with_rates.html',
        'runs_with_rates_per_plan_build': 'report/testrun_report_by_plan_build_with_rates.html',
    }
    errors  = None
    queries = request.GET
    data    = {}
    report_type = queries.get('report_type')
    PRODUCT_CHOICE = [
            (p.pk, p.name) for p in cached_entities('product')
        ]
    if queries:
        run_form = RunForm(queries)
        run_form.populate(queries)
        if run_form.is_valid():
            queries = run_form.cleaned_data
            data = test_run_report(queries, report_type)
        else:
            errors = run_form.errors
    tmpl = templates.get(report_type, 'report/common/search_run.html')
    queries = fmt_queries(queries)
    request_path = remove_from_request_path(request, 'report_type')
    if request_path:
        path_without_build = remove_from_request_path(request_path, 'r_build')
    data.update(locals())
    return direct_to_template(request, tmpl, data)
