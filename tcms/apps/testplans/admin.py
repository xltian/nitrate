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

from django.contrib import admin
from tcms.apps.testplans.models import TestPlanType
from tcms.apps.testplans.models import TestPlan

class TestPlanTypeAdmin(admin.ModelAdmin):
    search_fields = (('name',))
    list_display = ('id', 'name', 'description')

class TestPlanAdmin(admin.ModelAdmin):
    #fieldsets=[
#(None,{'fields':['name']}),
#('TestPlan Information',{'fields':['create_date']}),
    search_fields =(('name',))
    list_filter=['owner','create_date']
    list_display=('name','create_date','owner','author','type')
#]

admin.site.register(TestPlanType, TestPlanTypeAdmin)
admin.site.register(TestPlan,TestPlanAdmin)
