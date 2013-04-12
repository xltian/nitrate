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

# FIXME: Use signal to handle log

import threading
import datetime

from tcms.integration.djqpid import Producer

# Reference from
# http://www.chrisdpratt.com/2008/02/16/signals-in-django-stuff-thats-not-documented-well/

class NewRunEmailThread(threading.Thread):
    def __init__(self, instance, is_created):
        self.instance = instance
        self.is_created = is_created
        threading.Thread.__init__(self)

    def run(self):
        # run update
        if self.is_created:
            self.instance.mail(
                # new_run.txt can use in testrun update
                template = 'mail/update_run.txt',
                subject = 'Test Run %s - %s has been updated' % (
                    self.instance.pk, self.instance.summary
                ),
                context = {'test_run': self.instance,}
            )
        # run create
        else:
            self.instance.mail(
                template = 'mail/new_run.txt',
                subject = 'New run create from plan %s: %s' % (
                    self.instance.plan_id, self.instance.summary
                ),
                context = {'test_run': self.instance,}
            )

def post_run_saved(sender, *args, **kwargs):
    instance = kwargs['instance']
    if kwargs.get('created'):
        # Send the mail to default tester for alert him/her
        is_created = None
        NewRunEmailThread(instance, is_created).start()
    else:
        # FIXME: Log, Plugin and other editing functions
        is_created = True
        NewRunEmailThread(instance, is_created).start()

def post_case_run_saved(sender, *args, **kwargs):
    instance = kwargs['instance']
    if kwargs.get('created'):
        tr = instance.run
        tr.update_completion_status(is_auto_updated=True)

def post_case_run_deleted(sender, **kwargs):
    instance = kwargs['instance']
    tr = instance.run
    tr.update_completion_status(is_auto_updated=True)

def post_update_handler(sender, **kwargs):
    instances = kwargs['instances']
    instance = instances[0]
    tr = instance.run
    tr.update_completion_status(is_auto_updated=True)

# new testrun created info for qpid
def qpid_run_created(sender, *args, **kwargs):
    tr = kwargs['instance']
    if kwargs.get('created'):
        run_create_info = {
            "plan_id": tr.plan_id,
            "run_id": tr.run_id,
            "errata_id": tr.errata_id,
            "when": datetime.datetime.now().strftime("%Y-%m-%d %X")
        }
        try:
            Producer().send(run_create_info, "testrun.created", False)
        except:
            pass

    else:
        # FIXME: Log, Plugin and other editing functions
        pass

# testrun progress/finish info for qpid
def qpid_run_progress(sender, *args, **kwargs):
    tcr = kwargs['instance']
    tr = tcr.run
    if not kwargs.get('created'):
        # testrun is progress
        run_info = {
            "plan_id": tr.plan_id,
            "run_id": tr.run_id,
            "errata_id": tr.errata_id,
            "when": datetime.datetime.now().strftime("%Y-%m-%d %X"),
        }

        if not tr.check_all_case_runs():
            # testrun is progress
            completed_percent =  str(tr.completed_case_run_percent) + "%"
            run_info["completed_percent"] = completed_percent
            try:
                MessageBus().send(run_info, "testrun.progress", False)
            except:
                pass

        else:
            # testrun is finished
            try:
                Producer().send(run_info, "testrun.finished", False)
            except:
                pass
    else:
        # FIXME: log, plugin and other editing functions
        pass
