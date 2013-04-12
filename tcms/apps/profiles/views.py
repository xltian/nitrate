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

from django.views.decorators.csrf import csrf_protect
from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.conf import settings
from django.utils import simplejson
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q

from tcms.core.utils.raw_sql import RawSQL
from tcms.apps.testcases.models import TestCase
from tcms.apps.testplans.models import TestPlan
from tcms.apps.testruns.models import TestRun
from tcms.apps.profiles.models import UserProfile, BookmarkCategory, Bookmark

from tcms.apps.profiles.forms import BookmarkForm, UserProfileForm

MODULE_NAME = 'profile'

#@user_passes_test(lambda u: u.username == username)
@login_required
def bookmark(request, username, template_name = 'profile/bookmarks.html'):
    """
    Bookmarks for the user
    """

    if username != request.user.username:
        return HttpResponseRedirect(reverse('django.contrib.auth.views.login'))
    else:
        up = {'user': request.user}

    class BookmarkActions(object):
        def __init__(self):
            self.ajax_response = {
                'rc': 0,
                'response': 'ok',
            }

        def add(self):
            form = BookmarkForm(request.REQUEST)
            if not form.is_valid():
                ajax_response = {
                    'rc': 1,
                    'response': form.errors.as_text(),
                }
                return HttpResponse(simplejson.dumps(ajax_response))

            form.save()
            return HttpResponse(simplejson.dumps(self.ajax_response))

        def add_category(self):
            pass

        def remove(self):
            pks = request.REQUEST.getlist('pk')
            bks = Bookmark.objects.filter(
                pk__in = pks,
                user = request.user,
            )
            bks.delete()

            return HttpResponse(simplejson.dumps(self.ajax_response))

        def render(self):
            if request.REQUEST.get('category'):
                bks = Bookmark.objects.filter(
                    user = request.user,
                    category_id = request.REQUEST['category']
                )
            else:
                bks = Bookmark.objects.filter(user = request.user)

            return direct_to_template(request, template_name, {
                'user_profile': up,
                'bookmarks': bks,
            })

        def render_form(self):
            query = request.GET.copy()
            query['a'] = 'add'
            form = BookmarkForm(initial=query)
            form.populate(user = request.user)
            return HttpResponse(form.as_p())

    action = BookmarkActions()
    func = getattr(action, request.REQUEST.get('a', 'render'))
    return func()

@login_required
@csrf_protect
def profile(request, username, template_name = 'profile/info.html'):
    """
    Edit the profiles of the user
    """

    try:
        u = User.objects.get(username = username)
    except ObjectDoesNotExist, error:
        raise Http404(error)

    try:
        up = u.get_profile()
    except ObjectDoesNotExist, error:
        up = u.profile.create()
    message = None
    form = UserProfileForm(instance=up)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=up)
        if form.is_valid():
            form.save()
            message = 'Information successfully updated.'
    return direct_to_template(request, template_name, {
        'user_profile': up,
        'form': form,
        'message': message,
    })

@login_required
def recent(request, username, template_name='profile/recent.html'):
    """
    List the recent plan/run.
    """

    if username != request.user.username:
        return HttpResponseRedirect(reverse('django.contrib.auth.views.login'))
    else:
        up = {'user': request.user}

    runs_query = {
        'people': request.user,
        'is_active': True,
        'status': 'running',
    }

    tps = TestPlan.objects.filter(Q(author=request.user) | Q(owner=request.user))
    tps = tps.order_by('-plan_id')
    tps = tps.select_related('product', 'type')
    tps = tps.extra(select={
        'num_runs': RawSQL.num_runs,
    })
    tps_active = tps.filter(is_active=True)
    trs = TestRun.list(runs_query)
    test_plans_disable_count = tps.count() - tps_active.count()

    return direct_to_template(request, template_name, {
        'module': MODULE_NAME,
        'user_profile': up,
        'test_plans_count': tps.count(),
        'test_plans_disable_count':test_plans_disable_count,
        'test_runs_count': trs.count(),
        'last_15_test_plans': tps_active[:15],
        'last_15_test_runs': trs[:15],
    })

@login_required
def redirect_to_profile(request):
    return HttpResponseRedirect(reverse('tcms.apps.profiles.views.recent', args=[request.user.username]))
