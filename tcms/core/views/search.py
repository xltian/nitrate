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

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def search(request):
    """
    Redirect to correct url of the search content
    """
    from django.db import models
    from django.core.exceptions import ObjectDoesNotExist

    request_content = request.REQUEST.get('search_content', '')
    request_type = request.REQUEST.get('search_type')

    # Get search contents
    search_types = {
        'plans': ('testplans', 'testplan', reverse('tcms.apps.testplans.views.all')),
        'runs': ('testruns', 'testrun', reverse('tcms.apps.testruns.views.all')),
        'cases': ('testcases', 'testcase', reverse('tcms.apps.testcases.views.all'))
    }

    search_type = search_types.get(request_type)

    app_label = search_type[0]
    model = search_type[1]
    base_search_url = search_type[2]

    # Try to get the object directly
    try:
        request_content = int(request_content)
        target = models.get_model(*[app_label, model])._default_manager.get(pk=request_content)
        url = '%s' % (
            reverse('tcms.apps.%s.views.get' % app_label, args=[target.pk]),
        )

        return HttpResponseRedirect(url)
    except ObjectDoesNotExist, error:
        pass
    except ValueError:
        pass

    # Redirect to search all page
    url = '%s?a=search&search=%s' % (base_search_url, request_content)

    return HttpResponseRedirect(url)
