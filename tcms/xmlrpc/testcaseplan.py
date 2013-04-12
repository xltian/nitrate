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
#   Jian Chen <jianchen@redhat.com>

from tcms.apps.testcases.models import TestCase, TestCasePlan
from tcms.apps.testplans.models import TestPlan
from tcms.core.utils.xmlrpc import XMLRPCSerializer
from django.core.exceptions import ObjectDoesNotExist

__all__ = ('get', 'update')

def get(request, case_id, plan_id):
    """
    Description: Used to load an existing test-case-plan from the database.

    Params:      $case_id - Integer: An integer representing the ID of the test case in the database.
                 $plan_id - Integer: An integer representing the ID of the test plan in the database.

    Returns:     A blessed TestCasePlan object hash

    Example:
    >>> TestCasePlan.get(81307, 3551)
    """
    try:
        tc = TestCase.objects.get(pk=case_id)
    except ObjectDoesNotExist, error:
        return error

    try:
        tp = TestPlan.objects.get(pk=plan_id)
    except ObjectDoesNotExist, error:
        return error

    try:
        tcp = TestCasePlan.objects.get(plan=tp, case=tc)
    except ObjectDoesNotExist, error:
        return error

    return XMLRPCSerializer(model=tcp).serialize_model()

def update(request, case_id, plan_id, sortkey):
    """
    Description: Updates the sortkey of the selected test-case-plan.

    Params:      $case_id - Integer: An integer representing the ID of the test case in the database.
                 $plan_id - Integer: An integer representing the ID of the test plan in the database.
                 $sortkey - Integer: An integer representing the ID of the sortkey in the database.

    Returns:     A blessed TestCasePlan object hash

    Example:
    # Update sortkey of selected test-case-plan to 450
    >>> TestCasePlan.update(81307, 3551, 450)
    """
    try:
        tc = TestCase.objects.get(pk=case_id)
    except ObjectDoesNotExist, error:
        return error

    try:
        tp = TestPlan.objects.get(pk=plan_id)
    except ObjectDoesNotExist, error:
        return error

    try:
        tcp = TestCasePlan.objects.get(plan=tp, case=tc)
    except ObjectDoesNotExist, error:
        return error

    if isinstance(sortkey, int):
        tcp.sortkey = sortkey
        tcp.save()

    return XMLRPCSerializer(model=tcp).serialize_model()


