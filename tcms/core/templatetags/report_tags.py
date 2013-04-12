from django import template
from django.template import Node, TemplateSyntaxError

register = template.Library()

@register.filter(name = 'percentage')
def percentage(fraction, population):
    try:
        return "%.1f%%" % ((float(fraction) / float(population)) * 100)
    except ZeroDivisionError, Exception:
        return '0%'