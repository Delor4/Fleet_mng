from django import template

register = template.Library()


@register.filter
def index(_list, i):
    return _list[int(i)]
