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
Update testrun.case_run_status by executing a sql
for each testrun in a testrun queryset
'''

from django.db import connection, transaction
from tcms.apps.testruns.models import TestRun

_SQL = '''UPDATE test_runs SET case_run_status = (
        SELECT
            group_concat(concat(a.status, ':', a.count)) AS status_count
        FROM (
            SELECT
                case_run_status_id AS status,
                count(*) AS count FROM test_case_runs
            WHERE
                run_id = %s
            GROUP BY case_run_status_id
            ORDER BY status
        ) AS a
    )
    WHERE run_id = %s;'''

def get_runs():
    runs = TestRun.objects.all()
    cursor = connection.cursor()
    for run in runs:
        sql = _SQL % (run.run_id, run.run_id)
        cursor.execute(sql)
        transaction.commit_unless_managed()

def main():
    get_runs()

if __name__ == '__main__':
    main()
