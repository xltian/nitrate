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

def email_plan_update(plan):
    recipients = get_plan_notification_recipients(plan)
    if len(recipients) == 0:
        return
    subject = u'TestPlan %s has been updated.' % plan.pk
    send_email_using_threading(settings.PLAN_EMAIL_TEMPLATE, subject, {'plan': plan}, recipients)

def email_plan_deletion(plan):
    recipients = get_plan_notification_recipients(plan)
    if len(recipients) == 0:
        return
    subject = u'TestPlan %s has been deleted.' % plan.pk
    send_email_using_threading(settings.PLAN_DELELE_EMAIL_TEMPLATE, subject, {'plan': plan}, recipients)

def get_plan_notification_recipients(plan):
    recipients = set()
    if plan.owner:
        if plan.emailing.auto_to_plan_owner:
            recipients.add(plan.owner.email)
    if plan.emailing.auto_to_plan_author:
        recipients.add(plan.author.email)
    if plan.emailing.auto_to_case_owner:
        case_authors = plan.case.values_list('author__email', flat=True)
        recipients.update(case_authors)
    if plan.emailing.auto_to_case_default_tester:
        case_testers = plan.case.values_list('default_tester__email', flat=True)
        recipients.update(case_testers)
    return filter(lambda e: bool(e), recipients)
