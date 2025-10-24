from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='replace_dash')
@stringfilter
def replace_dash(value):
    """
    Replace all dashes with spaces
    Usage: {{ value|replace_dash }}
    """
    return value.replace('-', ' ') if value else ''
