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
#   Chaobin Tang <ctang@redhat.com>

'''
Generate testcases.xml used by pylot
www.pylot.org
'''

from tcms.apps.testplans.models import TestPlan

_HOSTNAME= 'http://chaobin-ubuntu.desktop:8080'

def get_plan_ids():
    plans = TestPlan.objects.all()
    plan_ids = plans.values_list('pk', flat=True)
    return plan_ids

def plan_testcase_generator(ids):
    for _id in ids:
        nodes = []
        nodes.append('<case><url>')
        url = '%s/plan/%s/' % (_HOSTNAME, _id)
        nodes.append(url)
        nodes.append('</url></case>')
        yield (''.join(nodes))

def get_plan_testcases():
    plan_ids = get_plan_ids()
    cases = []
    cases.append('<testcases>')
    cases.extend(list(plan_testcase_generator(plan_ids)))
    cases.append('</testcases>')
    return (''.join(cases))

def write_to_file(filename, content):
    f = open(filename, 'w')
    f.write(content)
    f.close()

def main():
    testcases = get_plan_testcases()
    write_to_file('plan_testcases.xml', testcases)

if __name__ == '__main__':
    main()

