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
A serializer to import/export between model objects and file formats.
'''

import csv
from lxml import etree


class TCR2File(object):
    '''
    Write TestCaseRun queryset into CSV or XML.
    '''
    ROOT = 'testcaseruns'
    HEADERS = ("Case Run ID", "Case ID",
        "Category", "Status", "Summary",
        "script", "Automated", "Log Link",
        "Bug IDs")

    def __init__(self, tcrs):
        self.root = self.ROOT
        self.headers = self.HEADERS
        self.tcrs = tcrs
        self.rows = []

    def tcr_attrs_in_a_list(self, tcr):
        line = [
            tcr.pk, tcr.case.pk, tcr.case.category,
            tcr.case_run_status, tcr.case.summary.encode('utf-8'),
            tcr.case.script, tcr.case.is_automated,
            self.log_links(tcr), self.bug_ids(tcr)
        ]
        return line

    def log_links(self, tcr):
        '''
        Wrap log links into a single cell by
        joining log links.
        '''
        log_links = tcr.links.all()
        return ' '.join(
            tcr.links.values_list('url', flat=True)
        )

    def bug_ids(self, tcr):
        '''
        Wrap bugs into a single cell by
        joining bug IDs.
        '''
        return ' '.join((
            str(pk) for pk in
            tcr.case.case_bug.values_list('bug_id', flat=True)
        ))

    def tcrs_in_rows(self):
        if self.rows: return self.rows
        for tcr in self.tcrs:
            row = self.tcr_attrs_in_a_list(tcr)
            self.rows.append(row)
        return self.rows

    def write_to_csv(self, fileobj):
        writer = csv.writer(fileobj)
        rows = self.tcrs_in_rows()
        writer.writerow(self.headers)
        writer.writerows(rows)

    def write_to_xml(self, fileobj):
        root = etree.Element(self.root)
        for tcr in self.tcrs:
            sub_elem = etree.Element('testcaserun')
            sub_elem.set('case_run_id', str(tcr.pk))
            sub_elem.set('case_id', str(tcr.case.pk))
            sub_elem.set('category', tcr.case.category.name or u'')
            sub_elem.set('status', str(tcr.case_run_status))
            sub_elem.set('summary', tcr.case.summary or u'')
            sub_elem.set('scripts', tcr.case.script or u'')
            sub_elem.set('automated', str(tcr.case.is_automated))
            log_sub_elem = etree.Element('loglinks')
            for link in tcr.links.all():
                log_sub_elem.set('name', link.name)
                log_sub_elem.set('url', link.url)
            sub_elem.append(log_sub_elem)
            bug_sub_elem = etree.Element('bugs')
            for bug in tcr.case.case_bug.all():
                bug_sub_elem.set('bug', str(bug.bug_id))
            sub_elem.append(bug_sub_elem)
            root.append(sub_elem)
        fileobj.write(etree.tostring(root))
