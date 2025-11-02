from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='i18n_content')
def i18n_content(content_dict, language='id'):
    """
    Extract language-specific content from a multilingual content dictionary.
    
    Supports two structures:
    1. Flat structure with language keys: {'id': 'value', 'en': 'value', 'zh': 'value'}
    2. Nested i18n structure: {'title': {'id': '...', 'en': '...', 'zh': '...'}}
    
    Falls back to Indonesian (id) if requested language not found.
    Falls back to original value if no i18n structure detected.
    
    Usage in template:
        {{ block.title|i18n_content:current_lang }}
        {{ block|i18n_content:current_lang }}
    """
    if not content_dict:
        return content_dict
    
    # Handle string input (already translated or non-i18n)
    if isinstance(content_dict, str):
        return content_dict
    
    # Handle dict with direct language keys
    if isinstance(content_dict, dict):
        # Check if this is a direct language dict (has 'id', 'en', or 'zh' keys)
        if 'id' in content_dict or 'en' in content_dict or 'zh' in content_dict:
            # Try requested language
            if language in content_dict:
                return content_dict[language]
            # Fallback to Indonesian
            if 'id' in content_dict:
                return content_dict['id']
            # Fallback to first available
            for lang in ['en', 'zh']:
                if lang in content_dict:
                    return content_dict[lang]
        
        # Not a language dict, return as is
        return content_dict
    
    # Return as is if not dict or string
    return content_dict


@register.filter(name='i18n_field')
def i18n_field(obj, field_and_lang):
    """
    Extract a specific field from an i18n-enabled object in the requested language.
    
    Usage:
        {{ block|i18n_field:"title,en" }}
        {{ block|i18n_field:"description,id" }}
    """
    if not obj or not field_and_lang:
        return ''
    
    try:
        field_name, language = field_and_lang.split(',')
        field_name = field_name.strip()
        language = language.strip()
    except ValueError:
        return ''
    
    if not isinstance(obj, dict):
        return ''
    
    field_value = obj.get(field_name)
    if not field_value:
        return ''
    
    return i18n_content(field_value, language)


@register.simple_tag(takes_context=True)
def i18n_block(context, block, field=''):
    """
    Template tag to extract language-aware content from a block.
    
    Usage:
        {% i18n_block block 'title' %}
        {% i18n_block block 'description' %}
    """
    current_lang = context.get('current_lang', 'id')
    
    if not block:
        return ''
    
    # If field specified, get that field first
    if field:
        if isinstance(block, dict):
            block = block.get(field, '')
        else:
            return ''
    
    # Apply i18n_content filter
    return i18n_content(block, current_lang)


@register.filter(name='i18n_items')
def i18n_items(items_list, language='id'):
    """
    Process a list of items and extract language-specific content from each.
    
    Usage:
        {% for item in block.items|i18n_items:current_lang %}
            {{ item.title }} - {{ item.description }}
        {% endfor %}
    """
    if not items_list:
        return []
    
    if not isinstance(items_list, list):
        return items_list
    
    processed_items = []
    for item in items_list:
        if isinstance(item, dict):
            processed_item = {}
            for key, value in item.items():
                processed_item[key] = i18n_content(value, language)
            processed_items.append(processed_item)
        else:
            processed_items.append(item)
    
    return processed_items


@register.filter(name='i18n_safe')
def i18n_safe(content_dict, language='id'):
    """
    Same as i18n_content but marks the output as safe HTML.
    Use this for rich text content.
    
    Usage:
        {{ block.description|i18n_safe:current_lang }}
    """
    result = i18n_content(content_dict, language)
    if isinstance(result, str):
        return mark_safe(result)
    return result
