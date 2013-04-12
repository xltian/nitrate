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

from django.db import models
from django.db.models.signals import post_save
from django.core.urlresolvers import reverse

from tcms.apps.testcases.models import TestCaseText, NoneText
from tcms.core.models import TCMSActionModel

from tcms.apps.testreviews import signals as review_watchers


# Create your models here.
class TestReview(TCMSActionModel):
    plan = models.ForeignKey('testplans.TestPlan', related_name='review')
    summary = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    author = models.ForeignKey('auth.User', related_name='review_author')
    build = models.ForeignKey('management.TestBuild', related_name='review_build')
    start_date = models.DateTimeField(auto_now_add=True)
    stop_date = models.DateTimeField(blank=True, null=True)

    default_reviewer = models.ManyToManyField(
        'auth.User',
        related_name='review_default_reviewer',
        blank=True,
        null=True,
    )

    env_value = models.ManyToManyField(
        'management.TCMSEnvValue',
        related_name='review_env',
        blank=True,
        null=True,
    )

    class Meta:
        db_table = u'tcms_reviews'
        ordering = ['-id']

    def add_case(self, case, sort_key = 0):
        self.review_case.create(
            case=case,
            case_text_version=case.latest_text().case_text_version,
            sort_key=sort_key,
        )

    def check_all_review_cases(self, review_case_id = None):
        trvcs = self.review_case.all()
        trvcs = trvcs.select_related('case__case_status')

        if review_case_id:
            for trvc in trvcs:
                if trvc.is_current:
                    trvc.is_current = False
                    trvc.save()

                if trvc.id == review_case_id:
                    trvc.is_current = True
                    trvc.save()

        for trvc in trvcs:
            if not trvc.is_finished():
                return False

        return True

    def get_absolute_url(self, request=None):
        # Upward compatibility code
        if request:
            return request.build_absolute_uri(
                reverse('tcms.apps.testreviews.views.get', args=[self.pk, ])
            )

        return self.get_url(request)

    def get_url_path(self):
        return reverse('tcms.apps.testreviews.views.get', args=[self.pk, ])

    def mail(self, template, subject, context, request=None):
        from tcms.core.utils.mailto import mailto

        to = [self.author.email]
        for dr in self.default_reviewer.all():
            to.append(dr.email)

        mailto(template, subject, to, context, request)

class TestReviewCase(TCMSActionModel):
    review = models.ForeignKey(TestReview, related_name='review_case')
    case = models.ForeignKey('testcases.TestCase', related_name='review_case')
    reviewer = models.ForeignKey(
        'auth.User',
        related_name='review_case_reviewer',
        blank=True,
        null=True
    )
    case_text_version = models.IntegerField()
    running_date = models.DateTimeField(auto_now_add=True)
    close_date = models.DateTimeField(null = True, blank=True)
    is_current = models.BooleanField(default=False)
    sort_key = models.IntegerField(default=0)
    class Meta:
        db_table = u'tcms_review_cases'
        ordering = ['sort_key', 'id']

    def get_text_with_version(self, case_text_version=None):
        if case_text_version:
            try:
                return TestCaseText.objects.get(
                    case__case_id=self.case_id,
                    case_text_version=case_text_version
                )
            except TestCaseText.DoesNotExist, error:
                return NoneText
        try:
            return TestCaseText.objects.get(
                case__case_id=self.case_id,
                case_text_version=self.case_text_version
            )
        except TestCaseText.DoesNotExist:
            return NoneText

    def is_finished(self):
        if self.case.case_status.name == 'PROPOSED':
            return False

        return True


# Signals handler
post_save.connect(review_watchers.post_review_saved, sender=TestReview)
