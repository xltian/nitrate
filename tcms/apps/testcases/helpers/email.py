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

# Authors:
#   Xuqing Kuang <xkuang@redhat.com>, Chaobin Tang <ctang@redhat.com>

# from django
from django.conf import settings

# from project
from tcms.core.utils.mailto import send_email_using_threading

def email_case_update(case):
    recipients = get_case_notification_recipients(case)
    cc = case.emailing.get_cc_list()
    if len(recipients) == 0:
        return
    subject = 'TestCase %s has been updated.' % case.pk
    txt = case.latest_text()
    context = {
        'test_case': case, 'test_case_text': txt,
        'test_case_plain_text': txt.get_plain_text(),
    }
    template = settings.CASE_EMAIL_TEMPLATE
    send_email_using_threading(template, subject, context, recipients, cc=cc)

def email_case_deletion(case):
    recipients = get_case_notification_recipients(case)
    cc = case.emailing.get_cc_list()
    if len(recipients) == 0:
        return
    subject = 'TestCase %s has been deleted.' % case.pk
    context = {
        'case': case,
    }
    template = settings.CASE_EMAIL_TEMPLATE
    send_email_using_threading(template, subject, context, recipients, cc=cc)

def get_case_notification_recipients(case):
    recipients = set()
    if case.emailing.auto_to_case_author:
        recipients.add(case.author.email)
    if case.emailing.auto_to_case_tester and case.default_tester:
        recipients.add(case.default_tester.email)
    if case.emailing.auto_to_run_manager:
        managers = case.case_run.values_list('run__manager__email', flat=True)
        recipients.update(managers)
    if case.emailing.auto_to_run_tester:
        run_testers = case.case_run.values_list('run__default_tester__email', flat=True)
        recipients.update(run_testers)
    if case.emailing.auto_to_case_run_assignee:
        assignees = case.case_run.values_list('assignee__email', flat=True)
        recipients.update(assignees)
    return filter(lambda e: bool(e), recipients)
