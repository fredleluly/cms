# Translation Guide - Matana University CMS

## Overview
This CMS supports 3 languages:
- **ID** (Bahasa Indonesia) - Default/fallback language
- **EN** (English)
- **ZH** (Chinese/中文)

## Two Types of Translation

### 1. Static UI Elements (Labels, Buttons, etc.)
Located in `/static/locales/*.json` files. Used for navigation, buttons, and static page elements.

### 2. Dynamic Content (Program Descriptions, etc.)
Stored in database ContentBlocks with multilingual JSON structure. Used for Program Studi content, articles, etc.

## Translation File Structure (Static UI)

Translation files are located in `/static/locales/`:
- `id.json` - Indonesian (Bahasa Indonesia)
- `en.json` - English
- `zh.json` - Chinese (中文)

## Translation Key Organization

Translation keys are organized by section:

### Navigation (`nav.*`)
Keys for main navigation menu items, programs, and faculties
```json
{
  "nav": {
    "profile": "Profil",
    "study_programs": "Program Studi",
    "faculty_business": "Fakultas Bisnis dan Pariwisata"
  }
}
```

### Footer (`footer.*`)
Keys for footer section headers and links
```json
{
  "footer": {
    "campus_services": "Layanan Kampus",
    "research": "Penelitian",
    "connect_with_us": "Connect With Us"
  }
}
```

### Common Elements (`common.*`)
Shared/reusable labels
```json
{
  "common": {
    "phone": "Telepon",
    "email": "Email",
    "address": "Alamat"
  }
}
```

### Page-Specific Sections
- `whatsapp.*` - WhatsApp chat bubble
- `home.*` - Home page specific labels
- `scholarship.*` - Scholarship page labels
- `news.*` - Generic news section labels
- `lppm.*` - LPPM-specific labels
- `lpm.*` - LPM-specific labels
- `mbkm.*` - MBKM-specific labels
- `mku.*` - MKU-specific labels
- `siak.*` - Academic system labels

## Using Translations in Templates

### Basic Usage
Add `data-i18n` attribute to any HTML element with the translation key:

```html
<h1 data-i18n="home.why_matana">Mengapa Matana University?</h1>
```

### For Attributes
Use `data-i18n-attr` to translate element attributes:

```html
<button 
  data-i18n="common.submit"
  data-i18n-attr="title"
>Submit</button>
```

### Best Practices

1. **Always include fallback text**: The Indonesian text should always be present in the HTML as fallback
   ```html
   <span data-i18n="nav.profile">Profil</span>
   ```

2. **Use semantic key names**: Keys should be descriptive and follow the pattern `section.element`
   ```
   Good: "scholarship.register_now"
   Bad: "button1", "text_a"
   ```

3. **Group related keys**: Keep related translations under the same section
   ```json
   {
     "scholarship": {
       "register_now": "...",
       "start_registration": "...",
       "register_opportunity": "..."
     }
   }
   ```

## Adding New Translations

### Step 1: Add to id.json (Indonesian)
```json
{
  "section_name": {
    "new_key": "Teks dalam Bahasa Indonesia"
  }
}
```

### Step 2: Add to en.json (English)
```json
{
  "section_name": {
    "new_key": "Text in English"
  }
}
```

### Step 3: Add to zh.json (Chinese)
```json
{
  "section_name": {
    "new_key": "中文文本"
  }
}
```

### Step 4: Use in Template
```html
<p data-i18n="section_name.new_key">Teks dalam Bahasa Indonesia</p>
```

## Language Switching

The language switcher is available in:
- Desktop: Top navigation bar (globe icon)
- Mobile: Mobile menu (top section)

Language preference is stored in browser localStorage and persists across sessions.

## Fallback Mechanism

If a translation key is not found:
1. System attempts to load from current language
2. If not found, falls back to Indonesian (id.json)
3. If still not found, displays the translation key itself

## Dynamic Content Exclusion

**Note**: Dynamic content from the database (e.g., News articles, blog posts) is NOT translated by this system. Only static UI elements are internationalized.

## Troubleshooting

### Translations not showing
1. Check browser console for errors
2. Verify JSON files are valid (use JSON validator)
3. Check that translation keys match exactly (case-sensitive)
4. Clear browser cache and localStorage

### Missing translations
1. Check all three locale files have the same keys
2. Verify the key path is correct (e.g., `nav.profile` not `navigation.profile`)

## Translation Tools

For translating text:
- Google Translate: Quick translations
- DeepL: Higher quality translations
- Professional review recommended for important UI text

## File Validation

Before committing changes, validate JSON files:
```bash
python3 -m json.tool static/locales/id.json
python3 -m json.tool static/locales/en.json
python3 -m json.tool static/locales/zh.json
```

## Dynamic Content Translation (Content Blocks)

For detailed information about translating dynamic content stored in the database (Program Studi descriptions, etc.), see:
- **[MULTILINGUAL_CONTENT_GUIDE.md](MULTILINGUAL_CONTENT_GUIDE.md)** - Complete guide for content block translation
- **[example_prodi_content_multilingual.json](example_prodi_content_multilingual.json)** - Example structure
- **[migrate_prodi_content.py](migrate_prodi_content.py)** - Migration script for existing content

Quick overview of content block translation:
1. Content blocks use nested JSON structure with `id`, `en`, `zh` keys
2. Use `data-i18n-content` attribute in templates to mark translatable content
3. JavaScript automatically switches content based on selected language
4. See MULTILINGUAL_CONTENT_GUIDE.md for complete instructions

## Contact

For translation-related questions or corrections, please contact the development team.
