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
from tcms.apps.testcases.models import TestCaseStatus, TestCaseCategory, TestCase
from tcms.apps.testcases.models import TestCaseBugSystem

class TestCaseStatusAdmin(admin.ModelAdmin):
    search_fields = (('name',))
    list_display = ('id', 'name', 'description')

class TestCaseCategoryAdmin(admin.ModelAdmin):
    search_fields = (('name',))
    list_display = ('id', 'name', 'product', 'description')
    list_filter = ('product', )

class TestCaseAdmin(admin.ModelAdmin):
    search_fields = (('summary',))
    list_display = ('case_id', 'summary', 'category', 'author', 'case_status')
    list_filter = ('case_status', 'category')

class TestCaseBugSystemAdmin(admin.ModelAdmin):
    search_fields = (('name',))
    list_display = ('id', 'name', 'url_reg_exp')

#admin.site.register(TestCaseStatus, TestCaseStatusAdmin)
admin.site.register(TestCaseCategory, TestCaseCategoryAdmin)
admin.site.register(TestCase, TestCaseAdmin)
admin.site.register(TestCaseBugSystem, TestCaseBugSystemAdmin)
