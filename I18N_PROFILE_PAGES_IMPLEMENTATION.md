# Internationalization Implementation for Profile Pages

## Overview
This implementation adds internationalization (i18n) support for content stored in `Page.content_blocks`, specifically for the Profil Matana, Manajemen, and Mitra pages. The solution allows dynamic content translation while maintaining backward compatibility with existing non-translated content.

## Implementation Details

### 1. JavaScript Module: `static/js/i18n-blocks.js`
**Purpose**: Handles client-side translation of HTML content blocks.

**Key Functions**:
- `applyBlockTranslations()`: Switches innerHTML of elements based on current language
- Reads from data attributes: `data-block-html-id`, `data-block-html-en`, `data-block-html-zh`
- Falls back to Indonesian (id) if translation not available
- Automatically called on page load and when language changes

**Usage**:
```html
<script src="{% static 'js/i18n-blocks.js' %}"></script>
```

### 2. Template Filters: `apps/pages/templatetags/i18n_filters.py`
**New Filters Added**:

#### `has_translations`
Checks if a block content dictionary contains all three translation keys (id, en, zh).

```django
{% if block.description|has_translations %}
    <!-- Render with translation data attributes -->
{% else %}
    <!-- Render normally -->
{% endif %}
```

#### `escape_html_attr`
Safely escapes HTML content for use in data attributes.

```django
data-block-html-en="{{ content.en|escape_html_attr }}"
```

### 3. Template Updates

#### `templates/pages/profile.html`
- Updated visi_misi_section to conditionally render with translation data attributes
- Updated sejarah_section to conditionally render with translation data attributes
- Added `i18n-blocks.js` script inclusion

**Example Pattern**:
```django
{% if blocks.sejarah_section.description|has_translations %}
<p class="text-gray-600 leading-relaxed text-lg"
   data-block-html-id="{{ blocks.sejarah_section.description.id|linebreaksbr|safe|escape_html_attr }}"
   data-block-html-en="{{ blocks.sejarah_section.description.en|linebreaksbr|safe|escape_html_attr }}"
   data-block-html-zh="{{ blocks.sejarah_section.description.zh|linebreaksbr|safe|escape_html_attr }}">
   {{ blocks.sejarah_section.description.id|safe|linebreaksbr }}
</p>
{% else %}
<p class="text-gray-600 leading-relaxed text-lg" data-i18n-content="sejarah_section.description">
   {{ blocks.sejarah_section.description|safe|linebreaksbr }}
</p>
{% endif %}
```

#### `templates/pages/prodi.html`
- Updated tujuan_section to support block translations
- Added `i18n-blocks.js` script inclusion

#### `templates/pages/management.html`
- Added `i18n-blocks.js` script inclusion
- Ready for modal content translation implementation

### 4. Views Updates: `apps/pages/views.py`

#### Profil Matana Page (`create_default_profile_page`)
**Updated Blocks**:
- `visi_misi_section`: Vision and Mission with Indonesian, English, and Chinese translations
- `sejarah_section`: History with full translations

**Translation Structure**:
```python
'description': {
    'id': 'Indonesian text...',
    'en': 'English text...',
    'zh': 'Chinese text...'
}
```

#### Management Page (`create_default_management_page`)
**Updated Example Profile**:
- Dr. Gregoria Illya's biography with full translations (as example)

### 5. Locale Files
**No changes needed** - existing locale files already contain necessary keys:
- `static/locales/id.json`
- `static/locales/en.json`
- `static/locales/zh.json`

Section keys like `profile.history`, `profile.vision_mission`, etc., are already defined.

## How It Works

### Translation Flow
1. **Page Load**: Django template renders HTML with default Indonesian content
2. **Data Attributes**: If translations exist, they're embedded as escaped HTML in data attributes
3. **JavaScript Activation**: `i18n-blocks.js` loads and applies translations based on current language
4. **Language Switch**: When user changes language, `applyBlockTranslations()` is called
5. **Content Update**: Elements with translation data attributes have their innerHTML updated

### Backward Compatibility
- Content blocks **without** translations display Indonesian content normally
- The `has_translations` filter ensures conditional rendering
- Existing admin-edited content remains unchanged
- No database migration required

## Usage for Content Editors

### Adding Translations to New Content
When creating default blocks in views.py, use this structure:

```python
{
    'identifier': 'my_section',
    'description': {
        'id': 'Teks Indonesia',
        'en': 'English text',
        'zh': '中文文本'
    }
}
```

### Admin-Edited Content
Content edited through Django admin will continue to work without translations. To add translations:
1. Structure the content field as a JSON object with id/en/zh keys
2. The template will automatically detect and apply translations

## Testing

### Manual Testing Steps
1. Navigate to `/profil-matana`
2. Check that content displays in Indonesian by default
3. Switch language to English using language selector
4. Verify Vision, Mission, and History sections update to English
5. Switch to Chinese and verify translations
6. Verify non-translated sections remain in Indonesian

### Verification Checklist
- [ ] Indonesian content displays correctly on page load
- [ ] English translations display when language switched to EN
- [ ] Chinese translations display when language switched to ZH
- [ ] Sections without translations remain in Indonesian (fallback)
- [ ] Line breaks preserved in multi-paragraph content
- [ ] No JavaScript errors in browser console
- [ ] Works on profile.html, prodi.html, and management.html

## Browser Support
- Modern browsers with ES6 support
- Falls back gracefully if JavaScript disabled (shows Indonesian)
- localStorage used for language preference persistence

## Performance Considerations
- Translations embedded in HTML (no additional AJAX requests)
- Data attributes escaped for security
- Minimal JavaScript overhead
- Caching-friendly (content embedded at render time)

## Security
- HTML content properly escaped using `escape_html_attr` filter
- Prevents XSS attacks through data attribute injection
- Safe for user-generated content

## Future Enhancements
- Add translation support for modal content in management.html
- Consider database-level translation storage for admin-edited content
- Add translation UI in Django admin for easier content management

## Related Issues
- Fixes #61: Profil Matana i18n
- Fixes #57: Management page i18n
- Fixes #53: Partners page i18n

## Files Changed
1. `static/js/i18n-blocks.js` (new)
2. `apps/pages/templatetags/i18n_filters.py` (updated)
3. `templates/pages/profile.html` (updated)
4. `templates/pages/prodi.html` (updated)
5. `templates/pages/management.html` (updated)
6. `apps/pages/views.py` (updated)
