# Administrator Guide: Managing Multilingual Program Studi Content

## Quick Start

### For New Program Studi Pages

When creating a new Program Studi page, structure the content blocks with multilingual support from the start.

**Example: Creating Hero Section**

In the Django Admin, when editing a ContentBlock with identifier `hero_section`, use this JSON structure:

```json
{
  "title": {
    "id": "Informatika",
    "en": "Informatics",
    "zh": "信息学"
  },
  "description": {
    "id": "Program studi yang fokus pada teknologi informasi",
    "en": "Study program focusing on information technology",
    "zh": "专注于信息技术的学习计划"
  },
  "background_image": "/static/images/prodi/hero.jpg",
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
    }
  ]
}
```

**Key Points:**
- Each text field becomes an object with `id`, `en`, and `zh` keys
- Non-text fields (like `background_image`) stay as strings
- Arrays of items: each item's text fields become multilingual objects

### For Existing Program Studi Pages

If you have existing Program Studi content that is only in Indonesian, you have two options:

#### Option 1: Manual Update (Recommended for single pages)

1. Open the page in Django Admin
2. Edit each ContentBlock
3. Convert text fields to multilingual format
4. Refer to `example_prodi_content_multilingual.json` for structure

#### Option 2: Use Migration Script (For multiple pages)

```bash
# Preview changes without saving
python3 migrate_prodi_content.py --dry-run

# Migrate specific program
python3 migrate_prodi_content.py --program-slug prodi-informatika

# Migrate all prodi pages
python3 migrate_prodi_content.py
```

After migration:
1. Review the content - look for `[TRANSLATE]` placeholders
2. Replace placeholders with actual translations
3. Test language switching on the website

## Content Block Structure by Section

### 1. Hero Section (`hero_section`)

```json
{
  "title": {"id": "...", "en": "...", "zh": "..."},
  "description": {"id": "...", "en": "...", "zh": "..."},
  "background_image": "/static/images/...",
  "items": [
    {
      "title": {"id": "...", "en": "...", "zh": "..."},
      "description": {"id": "...", "en": "...", "zh": "..."}
    }
  ]
}
```

**What to translate:**
- title: Program name
- description: Program description
- items[].title: Stat labels (e.g., "Akreditasi", "Mahasiswa Aktif")
- items[].description: Stat values (usually numbers, may not need translation)

### 2. Visi Misi Section (`visi_misi_section`)

```json
{
  "background_image": "/static/images/...",
  "items": [
    {
      "title": {"id": "Visi", "en": "Vision", "zh": "愿景"},
      "description": {"id": "Vision statement...", "en": "...", "zh": "..."}
    },
    {
      "title": {"id": "Misi", "en": "Mission", "zh": "使命"},
      "description": {
        "id": "Mission 1\nMission 2\nMission 3",
        "en": "Mission 1\nMission 2\nMission 3",
        "zh": "使命1\n使命2\n使命3"
      }
    }
  ]
}
```

**Special Note on Missions:**
- Missions are separated by newlines (`\n`)
- Each mission point should be on a new line
- Keep the same number of mission points across all languages

### 3. Tujuan Section (`tujuan_section`)

```json
{
  "title": {
    "id": "Tujuan Program Studi",
    "en": "Study Program Objectives",
    "zh": "学习计划目标"
  },
  "description": {
    "id": "Program ini bertujuan untuk:<br><br>1. Tujuan pertama<br><br>2. Tujuan kedua",
    "en": "This program aims to:<br><br>1. First objective<br><br>2. Second objective",
    "zh": "本课程旨在：<br><br>1. 第一个目标<br><br>2. 第二个目标"
  }
}
```

**What to translate:**
- title: Section heading
- description: Full text with HTML formatting (keep `<br>` tags)

### 4. Konsentrasi Section (`konsentrasi_section`)

```json
{
  "items": [
    {
      "title": {"id": "Software Engineering", "en": "...", "zh": "..."},
      "description": {"id": "Fokus pada...", "en": "...", "zh": "..."}
    }
  ]
}
```

### 5. Kurikulum Section (`kurikulum_section`)

```json
{
  "items": [
    {
      "title": {"id": "Pemrograman Dasar", "en": "...", "zh": "..."},
      "description": {"id": "Optional description", "en": "...", "zh": "..."}
    }
  ]
}
```

### 6. Peluang Karir Section (`peluang_karir_section`)

```json
{
  "items": [
    {
      "title": {"id": "Software Developer", "en": "...", "zh": "..."},
      "description": {"id": "Optional description", "en": "...", "zh": "..."}
    }
  ]
}
```

## Translation Guidelines

### Academic Terms

Maintain consistency in translating academic terms:

| Indonesian | English | Chinese |
|------------|---------|---------|
| Program Studi | Study Program | 学习计划 |
| Sarjana | Bachelor's | 学士 |
| Magister | Master's | 硕士 |
| Dosen | Lecturer | 讲师 |
| Mahasiswa | Student | 学生 |
| Akreditasi | Accreditation | 认证 |
| Kurikulum | Curriculum | 课程 |
| Mata Kuliah | Course/Subject | 科目 |

### Quality Checklist

Before publishing translations:

- [ ] All three languages (id, en, zh) are complete
- [ ] No `[TRANSLATE]` placeholders remain
- [ ] Academic terms are consistent
- [ ] HTML tags (if any) are preserved in all versions
- [ ] Newlines are preserved for mission statements
- [ ] Numbers and proper nouns are consistent across languages
- [ ] Text length is reasonable (avoid huge discrepancies)

## Testing Your Changes

### 1. In Django Admin

1. Save your changes
2. View the page on the website
3. Switch between languages using the language selector
4. Verify all content updates correctly

### 2. Check Browser Console

Open browser developer tools (F12) and check for:
- JavaScript errors
- Missing translation warnings
- Content loading issues

### 3. Verify All Sections

Test each section of the page:
- Hero section title and description
- Vision and Mission statements  
- Program objectives
- Concentration areas
- Curriculum items
- Career opportunities

## Common Issues and Solutions

### Issue: Content doesn't change when switching languages

**Possible causes:**
1. Content block is not in multilingual format
2. JavaScript not loading properly
3. Browser cache

**Solutions:**
1. Check JSON structure matches the examples
2. Clear browser cache (Ctrl+Shift+R)
3. Check browser console for errors

### Issue: Some text shows but others don't

**Possible cause:** JSON syntax error

**Solution:** 
1. Validate your JSON using online validator
2. Check for missing commas, brackets, or quotes
3. Ensure all text fields have all three language versions

### Issue: Mission points not updating

**Possible cause:** Newline format issue

**Solution:**
- Ensure mission points are separated by `\n` (not just line breaks in the text editor)
- Each language version should have the same number of `\n` separators

## Getting Translation Help

### For Indonesian ↔ English
- Use DeepL or professional translation service
- Maintain formal academic tone
- Have a native speaker review if possible

### For Chinese (中文)
- Use professional translation service recommended
- Use Simplified Chinese (not Traditional)
- Ensure academic terminology is appropriate

### For Technical Terms
- Many technical terms (e.g., "Software Engineering", "Data Science") can remain in English
- Or provide localized versions based on common usage in that country

## Backup Before Major Changes

Before making significant changes to content:

1. Export current content (use Django admin)
2. Save a copy of the JSON
3. Make changes
4. Test thoroughly before publishing

## Need Help?

For questions or assistance:
1. Check `MULTILINGUAL_CONTENT_GUIDE.md` for technical details
2. See `example_prodi_content_multilingual.json` for complete example
3. Contact the development team

---

**Last Updated:** 2025-11-02
**Version:** 1.0
