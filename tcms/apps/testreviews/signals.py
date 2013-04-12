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

# Reference from
# http://www.chrisdpratt.com/2008/02/16/signals-in-django-stuff-thats-not-documented-well/

class NewReviewEmailThread(threading.Thread):
    def __init__(self, instance):
        self.instance = instance
        threading.Thread.__init__(self)
        
    def run(self):
        # The actual code we want to run
        self.instance.mail(
            template = 'mail/new_review.txt',
            subject = 'New review create from plan %s: %s' % (
                self.instance.plan_id, self.instance.summary
            ),
            context = { 'test_review': self.instance, }
        )

def post_review_saved(sender, *args, **kwargs):
    instance = kwargs['instance']
    if 'created' in kwargs:
        # Send the mail to default tester for alert him/her
        NewReviewEmailThread(instance).start()
