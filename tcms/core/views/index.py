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

def index(request, template_name = 'index.html'):
    """
    Home page of TCMS
    """

    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('django.contrib.auth.views.login'))

    return HttpResponseRedirect(
        reverse('tcms.apps.profiles.views.recent', args=[request.user.username])
    )
