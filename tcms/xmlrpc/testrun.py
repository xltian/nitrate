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
#   Xuqing Kuang <xkuang@redhat.com>, Chenxiong Qi <cqi@redhat.com>

from kobo.django.xmlrpc.decorators import user_passes_test, login_required, log_call
from django.core.exceptions import ObjectDoesNotExist
from tcms.apps.testcases.models import TestCase
from tcms.apps.testruns.models import TestRun, TestCaseRun
from tcms.apps.management.models import TestTag
from utils import pre_process_ids

__all__ = (
    'add_cases',
    'remove_cases',
    'add_tag',
    'create',
    'env_value',
    'filter',
    'filter_count',
    'get',
    'get_bugs',
    'get_change_history',
    'get_completion_report',
    'get_env_values',
    'get_tags',
    'get_test_case_runs',
    'get_test_cases',
    'get_test_plan',
    'remove_tag',
    'update',
    'link_env_value',
    'unlink_env_value'
)

@log_call
@user_passes_test(lambda u: u.has_perm('testruns.add_testcaserun'))
def add_cases(request, run_ids, case_ids):
    """
    Description: Add one or more cases to the selected test runs.

    Params:      $case_ids - Integer/Array/String: An integer or alias representing the ID in the database,
                                                  an arry of case_ids or aliases, or a string of comma separated case_ids.

                 $run_ids - Integer/Array/String: An integer representing the ID in the database
                                                  an array of IDs, or a comma separated list of IDs.

    Returns:     Array: empty on success or an array of hashes with failure
                        codes if a failure occured.

    Example:
    # Add case id 54321 to run 1234
    >>> TestRun.add_cases(1234, 54321)
    # Add case ids list [1234, 5678] to run list [56789, 12345]
    >>> TestRun.add_cases([56789, 12345], [1234, 5678])
    # Add case ids list '1234, 5678' to run list '56789, 12345' with String
    >>> TestRun.add_cases('56789, 12345', '1234, 5678')
    """
    trs = TestRun.objects.filter(run_id__in = pre_process_ids(run_ids))
    tcs = TestCase.objects.filter(case_id__in = pre_process_ids(case_ids))

    for tr in trs:
        for tc in tcs:
            tr.add_case_run(case = tc)

    return

@log_call
@user_passes_test(lambda u: u.has_perm('testruns.delete_testcaserun'))
def remove_cases(request, run_ids, case_ids):
    """
    Description: Remove one or more cases from the selected test runs.

    Params:      $run_ids - Integer/Array/String: An integer representing the ID in the database
                                                  an array of IDs, or a comma separated list of IDs.

                 $case_ids - Integer/Array/String: An integer or alias representing the ID in the database,
                                                  an arry of case_ids or aliases, or a string of comma separated case_ids.

    Returns:     Array: empty on success

    Exception:   When any exception is thrown on the server side, it will be
                 returned as JSON, which contains two items:

                 - status: 1.

                 - message: str, any message specific to the error on the server

    Example:
    # Remove case 54321 from run 1234
    >>> TestRun.remove_cases(1234, 54321)
    # Remove case ids list [1234, 5678] from run list [56789, 12345]
    >>> TestRun.remove_cases([56789, 12345], [1234, 5678])
    # Remove case ids list '1234, 5678' from run list '56789, 12345' with String
    >>> TestRun.remove_cases('56789, 12345', '1234, 5678')
    """

    try:
        trs = TestRun.objects.filter(run_id__in=pre_process_ids(run_ids))

        for tr in trs:
            crs = TestCaseRun.objects.filter(run=tr, case__in=pre_process_ids(case_ids))
            crs.delete()

    except Exception, err:
        message = '%s: %s' % (err.__class__.__name__, err.message)
        return { 'status': 1, 'message': message }

@log_call
@user_passes_test(lambda u: u.has_perm('testruns.add_testruntag'))
def add_tag(request, run_ids, tags):
    """
    Description: Add one or more tags to the selected test runs.

    Params:      $run_ids - Integer/Array/String: An integer representing the ID in the database,
                                                  an arry of run_ids, or a string of comma separated run_ids.

                 $tags - String/Array - A single tag, an array of tags,
                                        or a comma separated list of tags.

    Returns:     Array: empty on success or an array of hashes with failure
                        codes if a failure occured.

    Example:
    # Add tag 'foobar' to run 1234
    >>> TestPlan.add_tag(1234, 'foobar')
    # Add tag list ['foo', 'bar'] to run list [12345, 67890]
    >>> TestPlan.add_tag([12345, 67890], ['foo', 'bar'])
    # Add tag list ['foo', 'bar'] to run list [12345, 67890] with String
    >>> TestPlan.add_tag('12345, 67890', 'foo, bar')
    """
    trs = TestRun.objects.filter(pk__in = pre_process_ids(value = run_ids))
    tags = TestTag.string_to_list(tags)

    for tag in tags:
        t, c = TestTag.objects.get_or_create(name = tag)
        for tr in trs:
            tr.add_tag(tag = t)

    return

@log_call
@user_passes_test(lambda u: u.has_perm('testruns.add_testrun'))
def create(request, values):
    """
    Description: Creates a new Test Run object and stores it in the database.

    Params:      $values - Hash: A reference to a hash with keys and values
                           matching the fields of the test run to be created.
      +-------------------+----------------+-----------+------------------------------------+
      | Field             | Type           | Null      | Description                        |
      +-------------------+----------------+-----------+------------------------------------+
      | plan              | Integer        | Required  | ID of test plan                    |
      | build             | Integer/String | Required  | ID of Build                        |
      | errata_id         | Integer        | Optional  | ID of Errata                       |
      | manager           | Integer        | Required  | ID of run manager                  |
      | summary           | String         | Required  |                                    |
      | product           | Integer        | Required  | ID of product                      |
      | product_version   | Integer        | Required  | ID of product version              |
      | default_tester    | Integer        | Optional  | ID of run default tester           |
      | plan_text_version | Integer        | Optional  |                                    |
      | estimated_time    | TimeDelta      | Optional  | HH:MM:MM                           |
      | notes             | String         | Optional  |                                    |
      | status            | Integer        | Optional  | 0:RUNNING 1:STOPPED  (default 0)   |
      | case              | Array/String   | Optional  | list of case ids to add to the run |
      | tag               | Array/String   | Optional  | list of tag to add to the run      |
      +-------------------+----------------+-----------+------------------------------------+

    Returns:     The newly created object hash.

    Example:
    >>> values = {'build': 384,
        'manager': 137,
        'plan': 137,
        'errata_id': 124,
        'product': 61,
        'product_version': 93,
        'summary': 'Testing XML-RPC for TCMS',
    }
    >>> TestRun.create(values)
    """
    from datetime import datetime
    from tcms.core import forms
    from tcms.apps.testruns.forms import XMLRPCNewRunForm

    if not values.get('product'):
        raise ValueError('Value of product is required')

    if values.get('case'):
        values['case'] = pre_process_ids(value = values['case'])

    form = XMLRPCNewRunForm(values)
    form.populate(product_id = values['product'])

    if form.is_valid():
        tr = TestRun.objects.create(
            product_version = form.cleaned_data['product_version'],
            plan_text_version = form.cleaned_data['plan_text_version'],
            stop_date = form.cleaned_data['status'] and datetime.now() or None,
            summary = form.cleaned_data['summary'],
            notes = form.cleaned_data['notes'],
            estimated_time = form.cleaned_data['estimated_time'],
            plan = form.cleaned_data['plan'],
            build = form.cleaned_data['build'],
            errata_id = form.cleaned_data['errata_id'],
            manager = form.cleaned_data['manager'],
            default_tester = form.cleaned_data['default_tester'],
        )

        if form.cleaned_data['case']:
            for c in form.cleaned_data['case']:
                tr.add_case_run(case = c)
                del c

        if form.cleaned_data['tag']:
            tags = form.cleaned_data['tag']
            if isinstance(tags, str):
                tags = [c.strip() for c in tags.split(',') if c]

            for tag in tags:
                t, c = TestTag.objects.get_or_create(name = tag)
                tr.add_tag(tag = t)
                del tag, t, c
    else:
        return forms.errors_to_list(form)

    return tr.serialize()

@log_call
@user_passes_test(lambda u: u.has_perm('testruns.change_tcmsenvrunvaluemap'))
def env_value(request, action, run_ids, env_value_ids):
    """
    Description: add/remove env values to the given runs, function is same as link_env_value/unlink_env_value

    Params:      $action        - String: 'add' or 'remove'.
                 $run_ids       - Integer/Array/String: An integer representing the ID in the database,
                                  an array of run_ids, or a string of comma separated run_ids.

                 $env_value_ids - Integer/Array/String: An integer representing the ID in the database,
                                  an array of env_value_ids, or a string of comma separated env_value_ids.

    Returns:     Array: empty on success or an array of hashes with failure
                        codes if a failure occured.

    Example:
    # Add env value 13 to run id 8748
    >>> TestRun.env_value('add', 8748, 13)
    """
    from tcms.apps.management.models import TCMSEnvValue

    trs = TestRun.objects.filter(pk__in = pre_process_ids(value = run_ids))
    evs = TCMSEnvValue.objects.filter(
        pk__in = pre_process_ids(value = env_value_ids)
    )

    for tr in trs:
        for ev in evs:
            try:
                func = getattr(tr, action + '_env_value')
                func(env_value = ev)
            except:
                pass

    return

def filter(request, values = {}):
    """
    Description: Performs a search and returns the resulting list of test runs.

    Params:      $values - Hash: keys must match valid search fields.

        +--------------------------------------------------------+
        |                 Run Search Parameters                  |
        +--------------------------------------------------------+
        |        Key          |          Valid Values            |
        | build               | ForeignKey: Build                |
        | cc                  | ForeignKey: Auth.User            |
        | env_value           | ForeignKey: Environment Value    |
        | default_tester      | ForeignKey: Auth.User            |
        | run_id              | Integer                          |
        | manager             | ForeignKey: Auth.User            |
        | notes               | String                           |
        | plan                | ForeignKey: Test Plan            |
        | summary             | String                           |
        | tag                 | ForeignKey: Tag                  |
        | product_version     | String: Product version          |
        +--------------------------------------------------------+

    Returns:     Array: Matching test runs are retuned in a list of run object hashes.

    Example:
    # Get all of runs contain 'TCMS' in summary
    >>> TestRun.filter({'summary__icontain': 'TCMS'})
    # Get all of runs managed by xkuang
    >>> TestRun.filter({'manager__username': 'xkuang'})
    # Get all of runs the manager name starts with x
    >>> TestRun.filter({'manager__username__startswith': 'x'})
    # Get runs contain the case ID 12345, 23456, 34567
    >>> TestRun.filter({'case_run__case__case_id__in': [12345, 23456, 34567]})
    """
    return TestRun.to_xmlrpc(values)

def filter_count(request, values = {}):
    """
    Description: Performs a search and returns the resulting count of runs.

    Params:      $query - Hash: keys must match valid search fields (see filter).

    Returns:     Integer - total matching runs.

    Example:
    # See TestRun.filter()
    """
    return TestRun.objects.filter(**values).count()

def get(request, run_id):
    """
    Description: Used to load an existing test run from the database.

    Params:      $run_id - Integer: An integer representing the ID of the run in the database

    Returns:     Hash: A blessed TestRun object hash

    Example:
    >>> TestRun.get(1193)
    """
    try:
        tr = TestRun.objects.get(run_id = run_id)
    except TestRun.DoesNotExist, error:
        return error
    response = tr.serialize()
    #get the xmlrpc tags
    tag_ids = tr.tag.values_list('id', flat=True)
    query = {'id__in': tag_ids}
    tags = TestTag.to_xmlrpc(query)
    #cut 'id' attribute off, only leave 'name' here
    tags_without_id = map(lambda x:x["name"], tags)
    #replace tag_id list in the serialize return data
    response["tag"] = tags_without_id
    return response

def get_bugs(request, run_ids):
    """
    *** FIXME: BUGGY IN SERIALISER - List can not be serialize. ***
    Description: Get the list of bugs attached to this run.

    Params:      $run_ids - Integer/Array/String: An integer representing the ID in the database
                                                  an array of integers or a comma separated list of integers.

    Returns:     Array: An array of bug object hashes.

    Example:
    # Get bugs belong to ID 12345
    >>> TestRun.get_bugs(12345)
    # Get bug belong to run ids list [12456, 23456]
    >>> TestRun.get_bugs([12456, 23456])
    # Get bug belong to run ids list 12456 and 23456 with string
    >>> TestRun.get_bugs('12456, 23456')
    """
    from tcms.apps.testcases.models import TestCaseBug
    trs = TestRun.objects.filter(
        run_id__in = pre_process_ids(value = run_ids)
    )
    tcrs = TestCaseRun.objects.filter(
        run__run_id__in = trs.values_list('run_id', flat = True)
    )

    query = {'case_run__case_run_id__in': tcrs.values_list('case_run_id', flat = True)}
    return TestCaseBug.to_xmlrpc(query)

def get_change_history(request, run_id):
    """
    *** FIXME: NOT IMPLEMENTED - History is different than before ***
    Description: Get the list of changes to the fields of this run.

    Params:      $run_id - Integer: An integer representing the ID of the run in the database

    Returns:     Array: An array of hashes with changed fields and their details.
    """
    pass

def get_completion_report(request, run_ids):
    """
    *** FIXME: NOT IMPLEMENTED ***
    Description: Get a report of the current status of the selected runs combined.

    Params:      $runs - Integer/Array/String: An integer representing the ID in the database
                        an array of integers or a comma separated list of integers.

    Returns:     Hash: A hash containing counts and percentages of the combined totals of
                        case-runs in the run. Counts only the most recently statused case-run
                        for a given build and environment.
    """
    pass

def get_env_values(request, run_id):
    """
    Description: Get the list of env values to this run.

    Params:      $run_id - Integer: An integer representing the ID of the run in the database

    Returns:     Array: An array of tag object hashes.

    Example:
    >>> TestRun.get_env_values(8748)
    """
    from tcms.apps.management.models import TCMSEnvValue
    query = {'testrun__pk': run_id}
    return TCMSEnvValue.to_xmlrpc(query)

def get_tags(request, run_id):
    """
    Description: Get the list of tags attached to this run.

    Params:      $run_id - Integer: An integer representing the ID of the run in the database

    Returns:     Array: An array of tag object hashes.

    Example:
    >>> TestRun.get_tags(1193)
    """
    try:
        tr = TestRun.objects.get(run_id = run_id)
    except:
        raise

    tag_ids = tr.tag.values_list('id', flat=True)
    query = {'id__in': tag_ids}
    return TestTag.to_xmlrpc(query)

def get_test_case_runs(request, run_id, is_current = None):
    """
    Description: Get the list of cases that this run is linked to.

    Params:      $run_id - Integer: An integer representing the ID in the database
                                    for this run.

                 $is_current - Boolean: True/1 to only include the current set (what is displayed
                                        in the web page) False/0: to return all, current and historical.

    Returns:     Array: An array of test case-run object hashes.

    Example:
    # Get all of case runs
    >>> TestRun.get_test_case_runs(1193)
    # Get the cases runs in executing
    >>> TestRun.get_test_case_runs(1193, 1)
    """
    query = {'run__run_id': run_id}
    if is_current is not None:
        query['is_current'] = is_current
    return TestCaseRun.to_xmlrpc(query)

def get_test_cases(request, run_id):
    """
    Description: Get the list of cases that this run is linked to.

    Params:      $run_id - Integer: An integer representing the ID in the database
                                    for this run.

    Returns:     Array: An array of test case object hashes.

    Example:
    >>> TestRun.get_test_cases(1193)
    """
    from tcms.apps.testcases.models import TestCase
    from tcms.core.utils.xmlrpc import XMLRPCSerializer

    try:
        tr = TestRun.objects.get(run_id=run_id)
    except ObjectDoesNotExist:
        raise

    tc_ids = tr.case_run.values_list('case_id', flat=True)
    tc_run_id = dict(tr.case_run.values_list('case_id', 'case_run_id'))
    tc_status = dict(tr.case_run.values_list('case_id', 'case_run_status__name'))
    tcs = TestCase.objects.filter(case_id__in=tc_ids)
    tcs_serializer = XMLRPCSerializer(tcs).serialize_queryset()
    for case in tcs_serializer:
        case['case_run_id'] = tc_run_id[case['case_id']]
        case['case_run_status'] = tc_status[case['case_id']]
    return tcs_serializer

def get_test_plan(request, run_id):
    """
    Description: Get the plan that this run is associated with.

    Params:      $run_id - Integer: An integer representing the ID in the database
                                    for this run.

    Returns:     Hash: A plan object hash.

    Example:
    >>> TestRun.get_test_plan(1193)
    """
    return TestRun.objects.select_related('plan').get(run_id = run_id).plan.serialize()

@log_call
@user_passes_test(lambda u: u.has_perm('testruns.delete_testruntag'))
def remove_tag(request, run_ids, tags):
    """
    Description: Remove a tag from a run.

    Params:      $run_ids - Integer/Array/String: An integer or alias representing the ID in the database,
                             an array of run_ids, or a string of comma separated run_ids.

                 $tag - String - A single tag to be removed.

    Returns:     Array: Empty on success.

    Example:
    # Remove tag 'foo' from run 1234
    >>> TestRun.remove_tag(1234, 'foo')
    # Remove tag 'foo' and 'bar' from run list [56789, 12345]
    >>> TestRun.remove_tag([56789, 12345], ['foo', 'bar'])
    # Remove tag 'foo' and 'bar' from run list '56789, 12345' with String
    >>> TestRun.remove_tag('56789, 12345', 'foo, bar')
    """
    trs = TestRun.objects.filter(
        run_id__in = pre_process_ids(value = run_ids)
    )
    tgs = TestTag.objects.filter(
        name__in = TestTag.string_to_list(tags)
    )

    for tr in trs:
        for tg in tgs:
            try:
                tr.remove_tag(tag = tg)
            except ObjectDoesNotExist:
                pass
            except:
                raise

    return

@log_call
@user_passes_test(lambda u: u.has_perm('testruns.change_testrun'))
def update(request, run_ids, values):
    """
    Description: Updates the fields of the selected test run.

    Params:      $run_ids - Integer/Array/String: An integer or alias representing the ID in the database,
                            an array of run_ids, or a string of comma separated run_ids.

                 $values - Hash of keys matching TestRun fields and the new values
                           to set each field to. See params of TestRun.create for description
                 +-------------------+----------------+--------------------------+
                 | Field             | Type           | Description              |
                 +-------------------+----------------+--------------------------+
                 | plan              | Integer        | TestPlan.plan_id         |
                 | product           | Integer        | Product.id               |
                 | build             | Integer        | Build.id                 |
                 | errata_id         | Integer        | Errata.id                |
                 | manager           | Integer        | Auth.User.id             |
                 | default_tester    | Intege         | Auth.User.id             |
                 | summary           | String         |                          |
                 | estimated_time    | TimeDelta      | MM/DD/YYYY               |
                 | product_version   | Integer        |                          |
                 | plan_text_version | Integer        |                          |
                 | notes             | String         |                          |
                 | status            | Integer        | 0:RUNNING 1:FINISHED     |
                 +-------------------+----------------+ -------------------------+
    Returns:     Hash: The updated test run object.

    Example:
    # Update status to finished for run 1193 and 1194
    >>> TestRun.update([1193, 1194], {'status': 1})
    """
    from datetime import datetime
    from tcms.core import forms
    from tcms.apps.testruns.forms import XMLRPCUpdateRunForm

    if (values.get('product_version') and not values.get('product')):
        raise ValueError('Field "product" is required by product_version')

    form = XMLRPCUpdateRunForm(values)
    if values.get('product_version'):
        form.populate(product_id = values['product'])

    if form.is_valid():
        trs = TestRun.objects.filter(pk__in = pre_process_ids(value = run_ids))

        if form.cleaned_data['plan']:
            trs.update(plan = form.cleaned_data['plan'])

        if form.cleaned_data['build']:
            trs.update(build = form.cleaned_data['build'])

        if form.cleaned_data['errata_id']:
            trs.update(errata_id = form.cleaned_data['errata_id'])

        if form.cleaned_data['manager']:
            trs.update(manager = form.cleaned_data['manager'])
        if values.has_key('default_tester'):
            if values.get('default_tester') and form.cleaned_data['default_tester']:
                trs.update(default_tester = form.cleaned_data['default_tester'])
            else:
                trs.update(default_tester = None)
        if form.cleaned_data['summary']:
            trs.update(summary = form.cleaned_data['summary'])

        if form.cleaned_data['estimated_time']:
            trs.update(estimated_time = form.cleaned_data['estimated_time'])

        if form.cleaned_data['product_version']:
            trs.update(product_version = form.cleaned_data['product_version'])

        if values.has_key('notes'):
            if values['notes'] in (None, ''):
                trs.update(notes = values['notes'])
            if form.cleaned_data['notes']:
                trs.update(notes = form.cleaned_data['notes'])

        if form.cleaned_data['plan_text_version']:
            trs.update(plan_text_version = form.cleaned_data['plan_text_version'])

        if isinstance(form.cleaned_data['status'], int):
            if form.cleaned_data['status']:
                trs.update(stop_date = datetime.now())
            else:
                trs.update(stop_date = None)
    else:
        return forms.errors_to_list(form)

    query = {'pk__in': trs.values_list('pk', flat=True)}
    return TestRun.to_xmlrpc(query)

@log_call
@user_passes_test(lambda u: u.has_perm('testruns.add_tcmsenvrunvaluemap'))
def link_env_value(request, run_ids, env_value_ids):
    """
    Description: Link env values to the given runs.

    Params:      $run_ids       - Integer/Array/String: An integer representing the ID in the database,
                                  an array of run_ids, or a string of comma separated run_ids.

                 $env_value_ids - Integer/Array/String: An integer representing the ID in the database,
                                  an array of env_value_ids, or a string of comma separated env_value_ids.

    Returns:     Array: empty on success or an array of hashes with failure
                        codes if a failure occured.

    Example:
    # Add env value 13 to run id 8748
    >>> TestRun.link_env_value(8748, 13)
    """
    return env_value(request, 'add', run_ids, env_value_ids)

@log_call
@user_passes_test(lambda u: u.has_perm('testruns.delete_tcmsenvrunvaluemap'))
def unlink_env_value(request, run_ids, env_value_ids):
    """
    Description: Unlink env values to the given runs.

    Params:      $run_ids       - Integer/Array/String: An integer representing the ID in the database,
                                  an array of run_ids, or a string of comma separated run_ids.

                 $env_value_ids - Integer/Array/String: An integer representing the ID in the database,
                                  an array of env_value_ids, or a string of comma separated env_value_ids.

    Returns:     Array: empty on success or an array of hashes with failure
                        codes if a failure occured.

    Example:
    # Unlink env value 13 to run id 8748
    >>> TestRun.unlink_env_value(8748, 13)
    """
    return env_value(request, 'remove', run_ids, env_value_ids)
