# -*- coding: utf-8 -*-

from django.db.models.signals import post_save, post_delete
from tcms.apps.testcases.models import TestCaseBug
from tcms.integration.apps.bugzilla.signals.bugs import bug_added_bz_handler

# Bug add/remove listen for bugzilla external_trackers
post_save.connect(bug_added_bz_handler, TestCaseBug)
