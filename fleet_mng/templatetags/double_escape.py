from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import escape

register = template.Library()


@register.filter
@stringfilter
def double_escape(string):
    return escape(escape(string))
