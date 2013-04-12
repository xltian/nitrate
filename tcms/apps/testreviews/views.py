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

from datetime import datetime
from django.contrib.auth.decorators import user_passes_test
from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404

from tcms.apps.testplans.models import TestPlan
from models import TestReview
from forms import NewReviewForm

# Create your views here.

@user_passes_test(lambda u: u.has_perm('testreviews.add_testreview'))
def new(request, plan_id, template_name='review/new.html'):
    """Create new test case review process"""
    try:
        tp = TestPlan.objects.get(plan_id = plan_id)
    except TestPlan.DoesNotExist, error:
        raise Http404(error)

    if request.method == 'POST':
        form = NewReviewForm(request.user, tp, request.REQUEST)

        if form.is_valid():
            trv = TestReview.objects.create(
                plan = tp,
                summary = form.cleaned_data['summary'],
                notes = form.cleaned_data['notes'],
                author = request.user,
                build = form.cleaned_data['build'],
            )

            if form.cleaned_data['default_reviewer']:
                try:
                    for default_reviewer in form.cleaned_data['default_reviewer']:
                        trv.default_reviewer.add(default_reviewer)
                except TypeError:
                    trv.default_reviewer.add(form.cleaned_data['default_reviewer'])

            for case in form.cleaned_data['case']:
                trv.add_case(case)

            for env_value in form.cleaned_data['env_value']:
                trv.env_value.add(env_value)

            return HttpResponseRedirect(reverse('tcms.apps.testreviews.views.get', args=[trv.id]))
    else:
        form = NewReviewForm(author = request.user, plan = tp)

    tcs = tp.case.select_related('author', 'case_status', 'category', 'priority')
    if request.REQUEST.get('case'):
        tcs = tcs.filter(case_id__in = request.REQUEST.getlist('case'))

    num_confirmed_cases = tcs.filter(case_status__name = 'CONFIRMED').count()

    return direct_to_template(request, template_name, {
        'testplan': tp,
        'testcases': tcs,
        'form': form,
        'num_confirmed_cases': num_confirmed_cases,
    })

def get(request, review_id, template_name='review/get.html'):
    """Display the review and change the case status"""
    from tcms.apps.testcases.models import TestCaseStatus

    try:
        trv = TestReview.objects.select_related(
            'author', 'default_reviewer', 'plan', 'plan__product',
        )
        trv = trv.get(id = review_id)
    except TestReview.DoesNotExist, error:
        raise Http404(error)

    trcs = trv.review_case.select_related(
        'case', 'case__author', 'case__case_status',
        'reviewer', 'case__case_status', 'case__priority'
    )

    return direct_to_template(request, template_name, {
        'test_review': trv,
        'test_review_cases': trcs,
        'test_case_status': TestCaseStatus.objects.all()
    })

@user_passes_test(lambda u: u.has_perm('testcases.change_testcase'))
def change_case_status(request, review_id, template_name='review/get_case.html'):
    """Change case review status"""
    from datetime import datetime
    from tcms.apps.testcases.models import TestCaseStatus

    if request.REQUEST.get('index_id'):
        forloop = {
            'counter': request.REQUEST['index_id']
        }
    else:
        return Http404('Index id is required')

    try:
        trv = TestReview.objects.get(id = review_id)
        trvc = trv.review_case.select_related('case', 'case_status')
        trvc = trvc.get(id = request.REQUEST.get('review_case_id'))
    except TestReview.DoesNotExist, error:
        raise Http404(error)

    if trvc.case.case_status_id == request.REQUEST.get('case_status_id'):
        return direct_to_template(request, template_name, {
            'forloop': forloop,
            'test_review_case': trvc,
            'message': 'No changes for the case.'
        })
    try:
        tc_status = TestCaseStatus.objects.get(
            id = request.REQUEST['case_status_id']
        )
    except TestCaseStatus.DoesNotExist, error:
        raise Http404(error)

    trvc.reviewer = request.user
    trvc.close_date = datetime.now()
    trvc.save()
    # Modify the case status and log the action
    tc = trvc.case

    tc.log_action(
        request.user,
        'Case status changed from %s to %s in review %s.' % (
            trvc.case.case_status, tc_status, trv.id
        )
    )

    tc.case_status = tc_status
    tc.save()

    # Check all of review cases status
    trv.check_all_review_cases(trvc.id)

    # Refresh the cached objects
    del trvc
    del tc

    trvc = trv.review_case.select_related(
        'case', 'case__author', 'case__case_status',
        'reviewer', 'case__case_status', 'case__priority'
    )
    trvc = trvc.get(id = request.REQUEST.get('review_case_id'))

    return direct_to_template(request, template_name, {
        'forloop': forloop,
        'test_review_case': trvc,
        'test_case_status': TestCaseStatus.objects.all()
    })
