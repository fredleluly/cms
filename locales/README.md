# Multi-Language (i18n) Implementation Guide

## Overview
This project now supports multi-language functionality with Indonesian (default), English, and Mandarin Chinese translations.

## Features
- ✅ Client-side translation system
- ✅ Three languages: Indonesian (ID), English (EN), Mandarin (ZH)
- ✅ Language preference persistence via localStorage
- ✅ Dynamic language switching without page reload
- ✅ Locale-aware date and number formatting using Intl API
- ✅ Non-invasive implementation - can be applied incrementally

## File Structure

```
cms/
├── locales/                    # Translation source files (for reference)
│   ├── id.json                # Indonesian translations
│   ├── en.json                # English translations
│   └── zh.json                # Mandarin translations
├── static/
│   ├── locales/               # Translation files served to client
│   │   ├── id.json
│   │   ├── en.json
│   │   └── zh.json
│   └── js/
│       └── i18n-init.js       # i18n initialization script
└── templates/
    └── base.html              # Updated with language selector
```

## Usage

### 1. Include i18n Script in Your Template

Add this to your HTML template's `<head>` or before `</body>`:

```html
<!-- i18n Support -->
<script src="{% static '/js/i18n-init.js' %}"></script>
```

### 2. Add Language Selector to Your UI

Example language selector (already added to `base.html`):

```html
<div class="language-selector">
  <a href="#" data-lang-switch="id">ID</a>
  <span>|</span>
  <a href="#" data-lang-switch="en">EN</a>
  <span>|</span>
  <a href="#" data-lang-switch="zh">中文</a>
</div>
```

### 3. Mark Elements for Translation

Add the `data-i18n` attribute to elements you want to translate:

```html
<!-- For text content -->
<span data-i18n="nav.profile">Profil</span>
<button data-i18n="common.apply">Daftar</button>

<!-- For attributes (placeholder, title, etc.) -->
<input type="text" 
       data-i18n="common.search" 
       data-i18n-attr="placeholder" 
       placeholder="Cari">
```

### 4. Translation Key Format

Keys use dot notation to access nested values:

```javascript
// In locale JSON files:
{
  "nav": {
    "profile": "Profil"  // Indonesian
  }
}

// In HTML:
data-i18n="nav.profile"
```

## Available Translation Keys

Check the locale JSON files for all available keys. Current structure:

- `nav.*` - Navigation items
- `profile.*` - Profile section
- `academics.*` - Academic section
- `admissions.*` - Admissions section
- `campus_life.*` - Campus life section
- `common.*` - Common UI elements
- `footer.*` - Footer elements
- `meta.*` - Meta descriptions

## JavaScript API

The i18n system is available globally as `window.i18n`:

```javascript
// Get current language
const currentLang = i18n.currentLang;

// Switch language programmatically
await i18n.switchLanguage('en');

// Get translation
const text = i18n.t('nav.profile');

// Format date
const formattedDate = i18n.formatDate(new Date());

// Format number
const formattedNumber = i18n.formatNumber(1234567.89);

// Format currency
const formattedCurrency = i18n.formatCurrency(15000000, 'IDR');
```

## Adding New Translations

1. **Add to JSON files**: Update `id.json`, `en.json`, and `zh.json` in both `/locales/` and `/static/locales/`
2. **Use consistent structure**: Ensure all three files have the same keys
3. **Add data-i18n attributes**: Mark the HTML elements to use the new translations

Example:

```json
// In all three locale files
{
  "common": {
    "save": "Simpan"  // id.json
    "save": "Save"    // en.json
    "save": "保存"    // zh.json
  }
}
```

```html
<!-- In HTML template -->
<button data-i18n="common.save">Simpan</button>
```

## Date and Number Formatting

The system uses the Intl API for locale-aware formatting:

### Date Formatting
```javascript
// Current locale format
const date = new Date();
const formatted = i18n.formatDate(date);

// Custom format options
const formatted = i18n.formatDate(date, {
  year: 'numeric',
  month: 'short',
  day: 'numeric'
});
```

### Number Formatting
```javascript
const number = 1234567.89;
const formatted = i18n.formatNumber(number, {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
});
```

### Currency Formatting
```javascript
const amount = 15000000;
const formatted = i18n.formatCurrency(amount, 'IDR');
```

## Events

The system dispatches a `languageChanged` event when language is switched:

```javascript
window.addEventListener('languageChanged', (event) => {
  console.log('Language changed to:', event.detail.lang);
  // Update your dynamic content here
});
```

## Backend Integration (Django)

For server-side rendering, consider using Django's built-in i18n:

1. Enable `USE_I18N = True` in settings.py
2. Use Django translation utilities for server-rendered content
3. Use `{% trans %}` and `{% blocktrans %}` tags in templates

For emails and SEO, server-side translation is recommended.

## Testing

A test page is available at `/static/i18n-test.html` for development purposes.

Run it with:
```bash
cd static
python -m http.server 8000
# Visit http://localhost:8000/i18n-test.html
```

## Browser Support

- Modern browsers with ES6+ support
- Intl API support (all modern browsers)
- localStorage support

## Troubleshooting

### Translations not loading
- Check browser console for errors
- Verify locale JSON files are accessible at `/static/locales/`
- Ensure JSON files are valid (use a JSON validator)

### Language not switching
- Check that `data-lang-switch` attributes are correct
- Verify localStorage is enabled in browser
- Check browser console for JavaScript errors

### Formatting not working
- Verify browser supports Intl API
- Check locale codes in LOCALE_MAP configuration
- Ensure correct locale format (e.g., 'id-ID', 'en-US', 'zh-CN')

## Future Enhancements

Consider adding:
- Traditional vs Simplified Chinese (`zh-TW` vs `zh-CN`)
- Right-to-left (RTL) language support
- Lazy loading of translation files
- Translation management interface
- Automated translation validation

## License

This i18n implementation is part of the Matana University CMS project.
