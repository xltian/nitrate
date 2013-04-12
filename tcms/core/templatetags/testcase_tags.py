from django import template
from django.template import Node, TemplateSyntaxError

from tcms.apps.testcases.models import TestCasePlan

register = template.Library()

@register.filter(name = 'sortkey')
def sortkey(case, plan):
    try:
        tcp = TestCasePlan.objects.get(plan = plan, case = case)
    except TestCasePlan.DoesNotExist:
        return None
    else:
        return tcp.sortkey

@register.filter(name = 'testcaseplan')
def testcaseplan(case, plan):
    try:
        tcp = TestCasePlan.objects.get(plan = plan, case = case)
    except TestCasePlan.DoesNotExist:
        return None
    else:
        return tcp.pk
