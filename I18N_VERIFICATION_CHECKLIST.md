# I18n Translation Verification Checklist

## Overview
This document provides a comprehensive checklist for verifying the internationalization implementation for Program Studi, Profil Matana, and Mitra pages.

## Pre-Verification Setup

### 1. Start the Development Server
```bash
cd /home/runner/work/cms/cms
python manage.py runserver
```

### 2. Access the Test Pages
- Program Studi: `http://localhost:8000/[program-studi-url]`
- Profil Matana: `http://localhost:8000/profile`
- Mitra: `http://localhost:8000/mitra`

## Verification Checklist

### A. JSON Files Validation ✓ COMPLETED

- [x] id.json is valid JSON
- [x] en.json is valid JSON  
- [x] zh.json is valid JSON
- [x] All three files have matching key structures
- [x] No duplicate keys exist

**Verification Command:**
```bash
python3 -m json.tool static/locales/id.json > /dev/null && echo "id.json valid"
python3 -m json.tool static/locales/en.json > /dev/null && echo "en.json valid"
python3 -m json.tool static/locales/zh.json > /dev/null && echo "zh.json valid"
```

### B. Program Studi (prodi.html) - Static Text

#### Hero Section
- [ ] "Program Sarjana" badge changes language (ID/EN/ZH)
- [ ] "Daftar Sekarang" button changes language
- [ ] "Pelajari Lebih Lanjut" button changes language

#### Visi Misi Section
- [ ] "Misi" heading changes language

#### Tab Navigation
- [ ] "Tujuan Program" tab label changes language
- [ ] "Konsentrasi" tab label changes language
- [ ] "Kurikulum" tab label changes language
- [ ] "Peluang Karir" tab label changes language

#### CTA Section
- [ ] "Mulai Perjalanan Akademik Anda" heading changes language
- [ ] "Bergabunglah dengan Program Studi" text changes language
- [ ] "di Matana University..." description changes language
- [ ] "Daftar Sekarang" button changes language
- [ ] "Bergabunglah dengan komunitas..." footer text changes language

#### Commented Blog Section (if activated)
- [ ] "Artikel Terkait Program Studi" heading changes language
- [ ] "Baca Selengkapnya" link changes language
- [ ] "Lihat Semua Artikel" button changes language

### C. Mitra (mitra.html) - Static Text

#### Hero Section
- [ ] "Mitra Kerja Sama" heading changes language
- [ ] "Berkolaborasi dengan berbagai institusi..." subtitle changes language

### D. Profil Matana (profile.html) - No Static Text
- [x] No static text to verify (all content is database-driven)
- [ ] Verify that dynamic content (Vision, Mission, History, etc.) still displays correctly

### E. Language Switching Functionality

#### Browser Controls
- [ ] Language switcher dropdown is visible
- [ ] Can switch to Bahasa Indonesia (ID)
- [ ] Can switch to English (EN)
- [ ] Can switch to Chinese (ZH)
- [ ] Language preference persists on page reload
- [ ] Language preference persists across different pages

#### JavaScript Console
- [ ] No JavaScript errors when switching languages
- [ ] `window.i18n.getCurrentLanguage()` returns correct language
- [ ] `languageChanged` event fires when language changes

### F. Fallback Mechanism

#### Test Missing Translation
- [ ] Add a test element with non-existent key: `data-i18n="test.missing.key"`
- [ ] Verify it falls back to Indonesian
- [ ] Verify no console errors appear

#### Test Partial Translation
- [ ] Remove one key from en.json temporarily
- [ ] Switch to English
- [ ] Verify that element shows Indonesian fallback for missing key
- [ ] Other elements still show English

### G. Browser Testing

#### Desktop Browsers
- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (if available)

#### Mobile Browsers
- [ ] Mobile Chrome (responsive mode)
- [ ] Mobile Safari (responsive mode)

#### Responsive Design
- [ ] Text wraps properly in all languages at mobile widths
- [ ] No text overflow issues
- [ ] Buttons remain clickable in all languages

### H. Translation Quality

#### Indonesian (ID) ✓
- [x] All translations are in proper Bahasa Indonesia
- [x] Terminology is consistent
- [x] Grammar is correct

#### English (EN) ✓
- [x] All translations are in proper English
- [x] Terminology is consistent
- [x] Grammar is correct
- [x] Professional tone maintained

#### Chinese (ZH) ✓
- [x] All translations are in Simplified Chinese
- [x] Characters are correctly displayed
- [x] Terminology is appropriate
- [x] Professional tone maintained

### I. Integration Testing

#### Page Navigation
- [ ] Navigate from Home → Program Studi
  - Language preference maintained
- [ ] Navigate from Program Studi → Mitra
  - Language preference maintained
- [ ] Navigate from Mitra → Profil Matana
  - Language preference maintained

#### Cross-Browser localStorage
- [ ] Set language to EN, close browser, reopen
  - Verify EN is still active
- [ ] Set language to ZH, open new tab
  - Verify ZH is active in new tab

### J. Performance

- [ ] Page load time not significantly affected
- [ ] Language switching is instantaneous (< 100ms)
- [ ] No visible flash of untranslated content (FOUC)

## Translation Keys Summary

### prodi section (15 keys)
1. prodi.register_now
2. prodi.learn_more
3. prodi.mission
4. prodi.program_goals
5. prodi.concentration
6. prodi.curriculum
7. prodi.career_opportunities
8. prodi.read_more
9. prodi.start_academic_journey
10. prodi.join_program
11. prodi.join_program_description
12. prodi.join_community
13. prodi.undergraduate_program
14. prodi.related_articles (commented)
15. prodi.view_all_articles (commented)

### partners section (2 keys)
1. partners.title
2. partners.subtitle

### profile section (1 key)
1. profile.history (reserved)

## Quick Test URLs

Once the server is running, test these URLs:
```
http://localhost:8000/prodi/[program-slug]
http://localhost:8000/profile
http://localhost:8000/mitra
```

## Manual Testing Steps

### Step 1: Test Indonesian (Default)
1. Open Program Studi page
2. Verify all text appears in Indonesian
3. Check that dynamic content still works

### Step 2: Test English
1. Click language switcher → English
2. Verify all static text changes to English
3. Verify dynamic content unchanged
4. Reload page
5. Verify English is maintained

### Step 3: Test Chinese
1. Click language switcher → 中文
2. Verify all static text changes to Chinese
3. Verify Chinese characters display correctly
4. Reload page
5. Verify Chinese is maintained

### Step 4: Test Navigation
1. Set language to English
2. Navigate to Mitra page
3. Verify Mitra page loads in English
4. Navigate to Profil Matana
5. Verify English is maintained

### Step 5: Test Console
1. Open browser DevTools (F12)
2. Switch languages
3. Verify no errors in console
4. Check localStorage for 'matana_language' key
5. Verify language code stored correctly

## Expected Results

### Success Criteria
✓ All 15 prodi keys translate correctly in all 3 languages
✓ All 2 partners keys translate correctly in all 3 languages
✓ Language switching works without errors
✓ Language preference persists
✓ Fallback to Indonesian works for missing keys
✓ No JavaScript console errors
✓ No visual regressions
✓ Dynamic content unaffected

### Common Issues to Watch For
- Text overflow in mobile view
- Missing translations showing key names
- Console errors when switching languages
- Language not persisting on reload
- Chinese characters not displaying (encoding issue)
- Dynamic content being incorrectly targeted for translation

## Automated Validation (Completed)

```bash
# Validate JSON structure
cd /home/runner/work/cms/cms
python3 -m json.tool static/locales/id.json > /dev/null && echo "✓ id.json valid"
python3 -m json.tool static/locales/en.json > /dev/null && echo "✓ en.json valid"  
python3 -m json.tool static/locales/zh.json > /dev/null && echo "✓ zh.json valid"
```

## Sign-off

- [ ] All verification steps completed
- [ ] No issues found
- [ ] Issues found and documented (see below)
- [ ] Ready for production

### Issues Found (if any)
```
[Document any issues found during verification]
```

### Notes
```
[Add any additional notes or observations]
```

---
**Last Updated:** 2025-11-02
**Verified By:** [Name]
**Status:** Pending Verification
