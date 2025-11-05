from django import template

register = template.Library()

@register.filter
def split_lines(text):
    if text:
        return text.split('\n')
    return []

@register.filter
def get_item(dictionary, key):
    if dictionary and key:
        return dictionary.get(key)
    return None

@register.filter
def get_index(list_or_dict, index):
    """Get item from list by index or from dict by key"""
    if not list_or_dict:
        return None
    try:
        # Try as list first
        if isinstance(list_or_dict, list):
            return list_or_dict[int(index)]
        # Try as dict
        elif isinstance(list_or_dict, dict):
            return list_or_dict.get(index)
    except (IndexError, ValueError, KeyError):
        pass
    return None 