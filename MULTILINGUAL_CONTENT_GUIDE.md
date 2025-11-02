# Multilingual Content Blocks Guide

## Overview
This guide explains how to structure ContentBlock data to support multiple languages (Indonesian, English, and Chinese) for Program Studi and other pages.

## Content Block Structure

### Single-Language Content (Current/Legacy)
```json
{
  "title": "Program Sarjana Informatika",
  "description": "Program studi yang fokus pada teknologi informasi",
  "items": [
    {
      "title": "Pemrograman",
      "description": "Belajar berbagai bahasa pemrograman"
    }
  ]
}
```

### Multilingual Content (New Format)
```json
{
  "title": {
    "id": "Program Sarjana Informatika",
    "en": "Bachelor of Informatics",
    "zh": "信息学学士课程"
  },
  "description": {
    "id": "Program studi yang fokus pada teknologi informasi",
    "en": "Study program focusing on information technology",
    "zh": "专注于信息技术的学习计划"
  },
  "items": [
    {
      "title": {
        "id": "Pemrograman",
        "en": "Programming",
        "zh": "编程"
      },
      "description": {
        "id": "Belajar berbagai bahasa pemrograman",
        "en": "Learn various programming languages",
        "zh": "学习各种编程语言"
      }
    }
  ]
}
```

## Implementation Methods

### Method 1: Using data-i18n-content Attribute (Recommended for Simple Text)

In your template:
```html
<h1 data-i18n-content="hero_section.title">Default Title</h1>
<p data-i18n-content="hero_section.description">Default description</p>
```

Required setup in template:
```html
<script>
// Make blocks available to JavaScript
window.pageBlocks = {{ blocks|safe }};
</script>
<script src="{% static 'js/i18n-content.js' %}"></script>
```

### Method 2: Using Template Filters (Server-Side)

Load the filter in your template:
```django
{% load i18n_filters %}
```

Use in template:
```django
<!-- For simple fields -->
<h1>{{ blocks.hero_section.title|i18n_content:current_lang }}</h1>

<!-- For HTML content (safe) -->
<div>{{ blocks.tujuan_section.description|i18n_safe:current_lang }}</div>

<!-- For lists of items -->
{% for item in blocks.konsentrasi_section.items|i18n_items:current_lang %}
    <h3>{{ item.title }}</h3>
    <p>{{ item.description }}</p>
{% endfor %}
```

### Method 3: Using Alpine.js (Reactive)

For pages already using Alpine.js:
```html
<div x-data="{ lang: 'id' }" x-init="lang = window.getCurrentLanguage()">
    <h1 x-text="getI18nContent(blocks.hero_section.title, lang)">Default</h1>
</div>
```

## Database Migration Strategy

### Option 1: Gradual Migration (Recommended)
Keep backward compatibility by supporting both formats:
- Old content: `"title": "Text"`
- New content: `"title": {"id": "Text", "en": "Text", "zh": "Text"}`

The i18n filters automatically detect and handle both formats.

### Option 2: Batch Update
Update all content blocks at once using a migration script.

Example migration script:
```python
from apps.pages.models import Page, ContentBlock

def migrate_prodi_content():
    """Convert single-language content to multilingual format"""
    pages = Page.objects.filter(template='prodi.html')
    
    for page in pages:
        for block in page.content_blocks.all():
            content = block.content
            
            # Example: Convert title
            if 'title' in content and isinstance(content['title'], str):
                old_title = content['title']
                content['title'] = {
                    'id': old_title,
                    'en': f"[EN] {old_title}",  # Placeholder
                    'zh': f"[ZH] {old_title}"   # Placeholder
                }
            
            block.save()
```

## Content Blocks That Need Translation

### For Program Studi Pages

1. **hero_section**
   - title (Program name)
   - description (Program description)
   - items (Statistics - title and description for each)

2. **visi_misi_section**
   - items[0].title (Vision heading)
   - items[0].description (Vision statement)
   - items[1].description (Mission points - newline separated)
   - background_image (no translation needed)

3. **tujuan_section**
   - title (Program Goals heading)
   - description (Goals description - may contain HTML)

4. **konsentrasi_section**
   - items (Array of concentration areas)
     - title (Concentration name)
     - description (Concentration description)

5. **kurikulum_section**
   - items (Array of curriculum items)
     - title (Subject/topic name)
     - description (Optional description)

6. **peluang_karir_section**
   - items (Array of career opportunities)
     - title (Job title/career path)
     - description (Optional description)

## Translation Workflow

### Step 1: Identify Content
List all fields that contain user-facing text in Indonesian.

### Step 2: Structure Multilingual JSON
Convert each text field to the multilingual format:
```json
{
  "field": {
    "id": "Indonesian text",
    "en": "English translation",
    "zh": "Chinese translation"
  }
}
```

### Step 3: Translate Content
- **Indonesian (id)**: Keep original content
- **English (en)**: Professional translation
- **Chinese (zh)**: Simplified Chinese translation

### Step 4: Update Template
Add appropriate i18n attributes or filters to display translated content.

### Step 5: Test
- Test language switching
- Verify all content updates correctly
- Check for missing translations (should fallback to Indonesian)

## Best Practices

1. **Always provide Indonesian (id)** - It's the fallback language
2. **Use consistent terminology** - Maintain a glossary for academic terms
3. **Keep structure consistent** - All language versions should have the same structure
4. **Test thoroughly** - Verify language switching works for all content
5. **Document placeholders** - Mark untranslated content clearly

## Example: Complete Hero Section

```json
{
  "identifier": "hero_section",
  "content": {
    "title": {
      "id": "Informatika",
      "en": "Informatics",
      "zh": "信息学"
    },
    "description": {
      "id": "Program studi yang mempersiapkan lulusan untuk menjadi profesional di bidang teknologi informasi dan komputer.",
      "en": "A study program that prepares graduates to become professionals in information technology and computing.",
      "zh": "一个旨在培养信息技术和计算机领域专业人才的学习计划。"
    },
    "background_image": "/static/images/prodi/informatika-hero.jpg",
    "items": [
      {
        "title": {
          "id": "Akreditasi",
          "en": "Accreditation",
          "zh": "认证"
        },
        "description": {
          "id": "A",
          "en": "A",
          "zh": "A"
        }
      },
      {
        "title": {
          "id": "Mahasiswa Aktif",
          "en": "Active Students",
          "zh": "在校学生"
        },
        "description": {
          "id": "500+",
          "en": "500+",
          "zh": "500+"
        }
      },
      {
        "title": {
          "id": "Dosen",
          "en": "Lecturers",
          "zh": "讲师"
        },
        "description": {
          "id": "25",
          "en": "25",
          "zh": "25"
        }
      }
    ]
  }
}
```

## Troubleshooting

### Content not updating on language switch
- Check that `window.pageBlocks` is properly initialized
- Verify `i18n-content.js` is loaded after `i18n-init.js`
- Check browser console for JavaScript errors

### Fallback not working
- Ensure Indonesian (id) version is always provided
- Check that content structure matches expected format

### Template filter not found
- Verify `{% load i18n_filters %}` is at the top of template
- Check that the templatetags directory has `__init__.py`

## Related Files
- `/static/js/i18n-init.js` - Core i18n system
- `/static/js/i18n-content.js` - Dynamic content handler
- `/apps/pages/templatetags/i18n_filters.py` - Django template filters
- `/static/locales/*.json` - Translation files for UI labels
