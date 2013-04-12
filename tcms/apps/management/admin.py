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
from tcms.apps.management.models import Classification, Product, Priority, Milestone, Component, Version
from tcms.apps.management.models import TestBuild, TestEnvironment, TestAttachment, TestTag

class ClassificationAdmin(admin.ModelAdmin):
    search_fields = ('name','pk',)
    list_display = ('id', 'name', 'description')

class ProductsAdmin(admin.ModelAdmin):
    search_fields = (('name','pk',))
    list_display = ('id', 'name', 'classification', 'description')
    list_filter = ('id', 'name', 'classification')
    exclude = ('milestone_url', 'default_milestone', 'vote_super_user', 'max_vote_super_bug')

class PriorityAdmin(admin.ModelAdmin):
    search_fields = (('value','pk',))
    list_display = ('id', 'value', 'sortkey', 'is_active')
    list_filter = ('is_active', )

class MilestoneAdmin(admin.ModelAdmin):
    search_fields = (('name','pk',))
    list_display = ('id', 'value', 'product', 'sortkey')
    list_filter = ('product', )

class ComponentAdmin(admin.ModelAdmin):
    search_fields = (('name','pk',))
    list_display = ('id', 'name', 'product', 'initial_owner', 'description')
    list_filter = ('product', )

class VersionAdmin(admin.ModelAdmin):
    search_fields = (('value','pk',))
    list_display = ('id', 'product', 'value')
    list_filter = ('product', )

class BuildAdmin(admin.ModelAdmin):
    search_fields = (('name','pk',))
    list_display = ('build_id', 'name', 'product', 'is_active')
    list_filter = ('product', )
    exclude = ('milestone',)

class AttachmentAdmin(admin.ModelAdmin):
    search_fields = (('file_name','pk',))
    list_display = ('attachment_id', 'file_name', 'submitter', 'description', 'create_date', 'mime_type')

admin.site.register(Classification, ClassificationAdmin)
admin.site.register(Product, ProductsAdmin)
admin.site.register(Priority, PriorityAdmin)
admin.site.register(Component, ComponentAdmin)
admin.site.register(Version, VersionAdmin)
admin.site.register(TestBuild, BuildAdmin)
