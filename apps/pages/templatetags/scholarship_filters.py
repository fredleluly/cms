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

@register.filter
def translate_to_en(value):
    """
    Extract English translation from multilingual content.
    If value is a dict with 'en' key, return that.
    Otherwise return the value as-is (fallback).
    """
    if isinstance(value, dict):
        return value.get('en', value.get('id', value))
    return value

@register.filter
def translate_to_zh(value):
    """
    Extract Chinese translation from multilingual content.
    If value is a dict with 'zh' key, return that.
    Otherwise return the value as-is (fallback).
    """
    if isinstance(value, dict):
        return value.get('zh', value.get('id', value))
    return value 