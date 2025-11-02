# Program Studi Multilingual Implementation - Quick Start Guide

## 📋 Overview

This implementation enables **complete multilingual support** (Indonesian/English/Chinese) for all Program Studi content, including:
- Program descriptions
- Vision and mission statements
- Program objectives
- Concentration areas
- Curriculum details
- Career opportunities

## 🚀 Quick Start (For Administrators)

### Step 1: Migrate Existing Content

```bash
# Preview what will change (safe, no modifications)
python3 migrate_prodi_content.py --dry-run

# Migrate a specific program
python3 migrate_prodi_content.py --program-slug prodi-informatika

# Or migrate all programs at once
python3 migrate_prodi_content.py
```

### Step 2: Add Translations

1. Open Django Admin
2. Navigate to the migrated ContentBlocks
3. Find `[TRANSLATE]` placeholders
4. Replace with actual English and Chinese translations
5. Refer to `example_prodi_content_multilingual.json` for examples

### Step 3: Test

1. Visit the Program Studi page
2. Use the language selector (ID/EN/ZH)
3. Verify all content updates correctly
4. Follow `TESTING_CHECKLIST.md` for comprehensive testing

## 📚 Documentation Guide

| Document | Who Should Read | What's Inside |
|----------|-----------------|---------------|
| **[ADMIN_MULTILINGUAL_GUIDE.md](ADMIN_MULTILINGUAL_GUIDE.md)** | Content Administrators | Step-by-step guide for managing multilingual content |
| **[MULTILINGUAL_CONTENT_GUIDE.md](MULTILINGUAL_CONTENT_GUIDE.md)** | Developers | Technical implementation details |
| **[I18N_PRODI_IMPLEMENTATION.md](I18N_PRODI_IMPLEMENTATION.md)** | Everyone | Complete implementation overview |
| **[TESTING_CHECKLIST.md](TESTING_CHECKLIST.md)** | QA/Testers | Comprehensive testing procedure |
| **[TRANSLATION_GUIDE.md](TRANSLATION_GUIDE.md)** | Translators | Translation guidelines |
| **[example_prodi_content_multilingual.json](example_prodi_content_multilingual.json)** | All | Example content structure |

## 🎯 Key Files

### For Developers
- `apps/pages/templatetags/i18n_filters.py` - Template filters
- `static/js/i18n-content.js` - JavaScript handler
- `templates/pages/prodi.html` - Updated template

### For Administrators
- `migrate_prodi_content.py` - Migration script
- `example_prodi_content_multilingual.json` - Content example
- `ADMIN_MULTILINGUAL_GUIDE.md` - Admin guide

### For QA/Testing
- `TESTING_CHECKLIST.md` - Testing checklist
- `check_i18n_keys.py` - Key consistency checker

## 🏗️ How It Works

### Content Structure

**Before (Single Language):**
```json
{
  "title": "Informatika",
  "description": "Program studi teknologi informasi"
}
```

**After (Multilingual):**
```json
{
  "title": {
    "id": "Informatika",
    "en": "Informatics",
    "zh": "信息学"
  },
  "description": {
    "id": "Program studi teknologi informasi",
    "en": "Information technology study program",
    "zh": "信息技术学习计划"
  }
}
```

### Language Switching

1. User clicks language selector
2. JavaScript updates all content
3. Changes happen instantly (no page reload)
4. Language preference is saved
5. Persists across page navigation

## ✅ Features

- ✅ **6 Content Sections** fully supported
- ✅ **3 Languages** (ID/EN/ZH)
- ✅ **Instant switching** (no page reload)
- ✅ **Automatic fallback** to Indonesian
- ✅ **HTML support** in content
- ✅ **Backward compatible** with existing content
- ✅ **Migration script** included
- ✅ **Comprehensive documentation**

## 🔍 Content Sections Covered

1. **Hero Section** - Title, description, statistics
2. **Visi/Misi** - Vision and mission statements
3. **Tujuan Program** - Program objectives
4. **Konsentrasi** - Concentration areas
5. **Kurikulum** - Curriculum items
6. **Peluang Karir** - Career opportunities

## 📖 Usage Examples

### Example 1: New Content

When creating new Program Studi content, use this structure:

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
      "id": "Program studi yang fokus pada teknologi informasi",
      "en": "Study program focusing on information technology",
      "zh": "专注于信息技术的学习计划"
    }
  }
}
```

### Example 2: Migrating Existing Content

```bash
# Step 1: Backup database
# Step 2: Run migration with dry-run
python3 migrate_prodi_content.py --dry-run --program-slug prodi-informatika

# Step 3: Review output
# Step 4: Apply migration
python3 migrate_prodi_content.py --program-slug prodi-informatika

# Step 5: Update translations in admin
```

## 🧪 Testing

Follow the comprehensive testing checklist:

```bash
# 1. Verify i18n keys are consistent
python3 check_i18n_keys.py

# 2. Follow testing checklist
# See: TESTING_CHECKLIST.md

# 3. Test in multiple browsers
# Chrome, Firefox, Safari

# 4. Test language switching
# ID → EN → ZH → ID
```

## 🛠️ Troubleshooting

### Content doesn't update when switching languages

**Check:**
1. Is content in multilingual format? (has `id`, `en`, `zh` keys)
2. Is JavaScript loading? (check browser console)
3. Clear browser cache (Ctrl+Shift+R)

### Some text shows, others don't

**Check:**
1. JSON syntax is valid
2. All text fields have all three languages
3. No missing commas or brackets

### Mission points not updating

**Check:**
1. Mission points are separated by `\n` (not just line breaks)
2. Same number of `\n` separators in all languages

See full troubleshooting guide in `ADMIN_MULTILINGUAL_GUIDE.md`

## 📞 Support

### For Different Roles

**Administrators:**
- Primary: `ADMIN_MULTILINGUAL_GUIDE.md`
- Example: `example_prodi_content_multilingual.json`

**Developers:**
- Primary: `MULTILINGUAL_CONTENT_GUIDE.md`
- Technical: `I18N_PRODI_IMPLEMENTATION.md`

**Translators:**
- Primary: `TRANSLATION_GUIDE.md`
- Guidelines: Academic term glossary in admin guide

**QA/Testers:**
- Primary: `TESTING_CHECKLIST.md`
- Tools: `check_i18n_keys.py`

## 🎓 Academic Terms Reference

| Indonesian | English | Chinese |
|------------|---------|---------|
| Program Studi | Study Program | 学习计划 |
| Sarjana | Bachelor's | 学士 |
| Visi | Vision | 愿景 |
| Misi | Mission | 使命 |
| Akreditasi | Accreditation | 认证 |
| Mahasiswa | Student | 学生 |
| Dosen | Lecturer | 讲师 |
| Kurikulum | Curriculum | 课程 |

## ⚙️ Technical Details

### Stack
- **Backend**: Django template filters
- **Frontend**: JavaScript (vanilla, no frameworks)
- **Storage**: JSON in ContentBlock model
- **Languages**: Indonesian, English, Simplified Chinese

### Files Modified
- `templates/pages/prodi.html` (updated)
- `TRANSLATION_GUIDE.md` (updated)

### Files Created
- `apps/pages/templatetags/i18n_filters.py`
- `static/js/i18n-content.js`
- `migrate_prodi_content.py`
- `example_prodi_content_multilingual.json`
- `ADMIN_MULTILINGUAL_GUIDE.md`
- `MULTILINGUAL_CONTENT_GUIDE.md`
- `I18N_PRODI_IMPLEMENTATION.md`
- `TESTING_CHECKLIST.md`
- This README

## 🚦 Status

- ✅ **Implementation**: Complete
- ✅ **Documentation**: Complete
- ✅ **Code Review**: Passed
- ⏳ **Testing**: Requires database content
- ⏳ **Deployment**: Pending testing

## 📅 Next Steps

1. **Populate Database** with multilingual content
2. **Test Thoroughly** using checklist
3. **Review Translations** for quality
4. **Deploy** to staging/production
5. **Monitor** for issues
6. **Scale** to other Program Studi pages

## 📄 License & Credits

- **Implementation**: GitHub Copilot
- **Date**: 2025-11-02
- **Version**: 1.0

---

**Need Help?** Choose your guide from the table above and start there!
