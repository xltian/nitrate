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
#   David Malcolm <dmalcolm@redhat.com>

# The following was obtained by clicking on "Remember values as bookmarkable template" in Bugzilla:

try:
    from html import html2text
except:
    raise

from tcms.apps.testcases.models import TestCaseText

test_url = "https://bugzilla.redhat.com/enter_bug.cgi?alias=&assigned_to=&attachurl=&blocked=&bug_file_loc=http%3A%2F%2F&bug_severity=medium&bug_status=NEW&cf_build_id=&cf_clone_of=&cf_cust_facing=---&cf_devel_whiteboard=&cf_internal_whiteboard=&cf_issuetracker=&cf_qa_whiteboard=&cf_targetrelease=---&comment=This%20is%20a%20test%20description&component=evolution&contenttypeentry=&contenttypemethod=autodetect&contenttypeselection=text%2Fplain&data=&deadline=&defined_cf_partner=&dependson=&description=&estimated_time=0.0&external_bug_id=&external_id=0&flag_type-10=X&flag_type-11=X&flag_type-15=X&flag_type-16=X&flag_type-160=X&flag_type-180=X&flag_type-186=X&flag_type-188=X&flag_type-24=X&flag_type-60=X&flag_type-9=X&form_name=enter_bug&keywords=&maketemplate=Remember%20values%20as%20bookmarkable%20template&op_sys=Linux&priority=low&product=Red%20Hat%20Enterprise%20Linux%205&qa_contact=&rep_platform=All&short_desc=This%20is%20a%20test%20summary&status_whiteboard=&target_milestone=rc&version=5.4"

class BugTracker(object):
    """
    Abstract base class representing an external bug tracking system
    """
    def make_url(self, caserun):
        raise NotImplementedError

class Bugzilla(BugTracker):
    def __init__(self, base_url):
        self.base_url = base_url

    def make_url(self, run, caserun, case_text_version):
        import urllib
        args = {}
        args['cf_build_id'] = run.build.name

        txt = caserun.get_text_with_version(case_text_version=case_text_version)

        if txt and isinstance(txt, TestCaseText):
            plain_txt = txt.get_plain_text()

            setup = plain_txt.setup
            action = plain_txt.action
            effect = plain_txt.effect
            breakdown = plain_txt.breakdown
        else:
            setup = 'None'
            action = 'None'
            effect = 'None'
            breakdown = 'None'

        comment = "Filed from caserun (INSERT URL HERE)\n\n"
        comment += "Version-Release number of selected component (if applicable):\n"
        comment += '%s\n\n' % caserun.build.name
        comment += "Steps to Reproduce: \n%s\n%s\n\n" % (setup, action)
        comment += "Actual results: \n#FIXME\n\n" #FIXME+ caseinfo['actual_results'] + "\n\n"
        comment += "Expected results:\n%s\n\n" % effect
        args['comment'] = comment
        args['component'] = caserun.case.component.values_list('name', flat=True)
        args['op_sys'] = 'Linux'
        args['product'] = run.plan.product.name
        args['short_desc'] = 'Test case failure: %s' % caserun.case.summary
        args['version'] = run.product_version
        args['bit-11'] = '1' # this should set the "only visible to Red Hat Quality Assurance (internal)" flag, but don't go filing this example bug.

        return self.base_url + 'enter_bug.cgi?' + urllib.urlencode(args, True)

cr = {'case_id':42,
      'build_name': 'THIS IS THE BUILD ID',
      'actions': 'Phase 1: Collect Underpants\nPhase 2: ?\nPhase 3: Profit!\n',
      'expected_results': 'Profit!',
      'actual_results': 'Kenny died',
      'component':'evolution',
      'product':'Red Hat Enterprise Linux 5',
      'summary':'This is a test case summary',
      'version':'5.4',
      }
#rh_bz = Bugzilla("https://bugzilla.redhat.com/")
#print rh_bz.make_url(cr)
# gives me:
# https://bugzilla.redhat.com/enter_bug.cgi?comment=Filed+from+caserun+%28INSERT+URL+HERE%29%0A%0AVersion-Release+number+of+selected+component+%28if+applicable%29%3A%0ATHIS+IS+THE+BUILD+ID%0A%0ASteps+to+Reproduce%3A%0APhase+1%3A+Collect+Underpants%0APhase+2%3A+%3F%0APhase+3%3A+Profit%21%0A%0A%0AActual+results%3A%0AKenny+died%0A%0AExpected+results%3A%0AProfit%21%0A%0A&product=Red+Hat+Enterprise+Linux+5&component=evolution&short_desc=This+is+a+test+case+summary&cf_build_id=THIS+IS+THE+BUILD+ID&version=5.4&op_sys=Linux&bit-11=1
# which has prepopulated the bug report

