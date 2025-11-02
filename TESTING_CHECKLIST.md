# Testing Checklist: Program Studi Multilingual Implementation

## Pre-Testing Setup

### 1. Database Preparation
- [ ] Backup current database
- [ ] Choose one Program Studi for initial testing (e.g., prodi-informatika)
- [ ] Review current content structure

### 2. Content Migration

#### Option A: Use Migration Script (Recommended)
```bash
# Step 1: Preview changes
python3 migrate_prodi_content.py --dry-run --program-slug prodi-informatika

# Step 2: Apply migration
python3 migrate_prodi_content.py --program-slug prodi-informatika

# Step 3: Review output - note blocks changed
```

#### Option B: Manual Update
- [ ] Open page in Django Admin
- [ ] For each ContentBlock, convert to multilingual format
- [ ] Use `example_prodi_content_multilingual.json` as reference

### 3. Translation
- [ ] Replace `[TRANSLATE]` placeholders with actual English translations
- [ ] Replace `[TRANSLATE]` placeholders with actual Chinese translations
- [ ] Verify Indonesian text is correct
- [ ] Review academic terminology consistency
- [ ] Check HTML tags are preserved

### 4. Deployment
- [ ] Clear application cache
- [ ] Restart Django server
- [ ] Clear browser cache
- [ ] Open browser DevTools (F12)

## Testing Procedure

### Phase 1: Basic Functionality

#### Test 1.1: Initial Page Load
- [ ] Navigate to Program Studi page
- [ ] Page loads without errors
- [ ] No JavaScript errors in console
- [ ] Content displays correctly

#### Test 1.2: Language Switching
- [ ] Click language selector
- [ ] Switch to English (EN)
  - [ ] All content updates to English
  - [ ] No console errors
  - [ ] Page doesn't reload
- [ ] Switch to Chinese (ZH)
  - [ ] All content updates to Chinese
  - [ ] No console errors
  - [ ] Page doesn't reload
- [ ] Switch back to Indonesian (ID)
  - [ ] Content returns to Indonesian
  - [ ] No console errors

#### Test 1.3: Language Persistence
- [ ] Select English
- [ ] Refresh page (F5)
- [ ] Language is still English
- [ ] Navigate to another page
- [ ] Return to Program Studi
- [ ] Language is still English
- [ ] Close and reopen browser
- [ ] Language preference persists

### Phase 2: Content Sections

#### Test 2.1: Hero Section
Switch between ID/EN/ZH and verify:
- [ ] Program title changes
- [ ] Program description changes
- [ ] Stat 1 label changes (e.g., "Akreditasi")
- [ ] Stat 2 label changes (e.g., "Mahasiswa Aktif")
- [ ] Stat 3 label changes (e.g., "Dosen")
- [ ] Stat values remain consistent

#### Test 2.2: Visi/Misi Section
Switch between ID/EN/ZH and verify:
- [ ] "Visi" heading changes
- [ ] Vision statement changes
- [ ] Mission heading stays as "Misi"/"Mission"/"使命"
- [ ] All mission points change (count them)
- [ ] Mission formatting preserved
- [ ] No blank mission points

#### Test 2.3: Tujuan Program Tab
- [ ] Click "Tujuan Program" tab
- [ ] Section title changes between languages
- [ ] Description text changes
- [ ] HTML formatting preserved (bullet points, line breaks)
- [ ] No broken HTML tags

#### Test 2.4: Konsentrasi Tab
- [ ] Click "Konsentrasi" tab
- [ ] Count concentration items
- [ ] For each item:
  - [ ] Title changes
  - [ ] Description changes (if present)
- [ ] All items display correctly

#### Test 2.5: Kurikulum Tab
- [ ] Click "Kurikulum" tab
- [ ] Count curriculum items
- [ ] For each item:
  - [ ] Title changes
  - [ ] Description changes (if present)
- [ ] Grid layout intact

#### Test 2.6: Peluang Karir Tab
- [ ] Click "Peluang Karir" tab
- [ ] Count career items
- [ ] For each item:
  - [ ] Title changes
  - [ ] Description changes (if present)
- [ ] All cards display correctly

### Phase 3: Edge Cases

#### Test 3.1: Missing Translations
Create a test block with incomplete translations:
```json
{
  "title": {
    "id": "Test",
    "en": "Test"
    // zh missing
  }
}
```
- [ ] Switch to Chinese
- [ ] Verify fallback to Indonesian works
- [ ] No JavaScript errors
- [ ] Content still displays

#### Test 3.2: Malformed Content
- [ ] Test with extra spaces in keys
- [ ] Test with empty strings
- [ ] Test with very long text
- [ ] Verify graceful handling

#### Test 3.3: Special Characters
Verify proper display of:
- [ ] Accented characters (é, ñ, etc.)
- [ ] Chinese characters (中文)
- [ ] Quotation marks ("", '', «»)
- [ ] Apostrophes (')
- [ ] Ampersands (&)

#### Test 3.4: HTML Content
- [ ] Line breaks (`<br>`) render correctly
- [ ] Bold text (`<b>`, `<strong>`) works
- [ ] Italics (`<i>`, `<em>`) works
- [ ] Lists (`<ul>`, `<ol>`) render properly
- [ ] No XSS vulnerabilities

### Phase 4: Performance

#### Test 4.1: Load Time
- [ ] Initial page load < 3 seconds
- [ ] Language switch < 500ms
- [ ] No visible flashing/flickering
- [ ] Smooth transitions

#### Test 4.2: Network
Open DevTools Network tab:
- [ ] Check requests made
- [ ] Verify locale files cached
- [ ] No redundant requests
- [ ] Reasonable payload sizes

#### Test 4.3: Console
Check browser console:
- [ ] No errors
- [ ] No warnings (or document expected ones)
- [ ] Appropriate logging level

### Phase 5: Cross-Browser Testing

#### Test 5.1: Desktop Browsers
Repeat Phase 1-2 tests in:
- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest, if available)

#### Test 5.2: Mobile Browsers
Test on mobile devices/emulators:
- [ ] Chrome Mobile
- [ ] Safari iOS
- [ ] Responsive design maintained
- [ ] Touch interactions work

#### Test 5.3: Screen Sizes
Test at different resolutions:
- [ ] Desktop (1920x1080)
- [ ] Laptop (1366x768)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)

### Phase 6: Accessibility

#### Test 6.1: Keyboard Navigation
- [ ] Tab through language selector
- [ ] Tab through all tabs
- [ ] Enter/Space keys work
- [ ] Focus indicators visible

#### Test 6.2: Screen Reader
Test with screen reader (if available):
- [ ] Content is read in selected language
- [ ] Language changes announced
- [ ] ARIA labels appropriate

## Issue Reporting

If any test fails, document:

### Issue Template
```markdown
**Test Failed:** [Test number and name]
**Expected:** [What should happen]
**Actual:** [What actually happened]
**Steps to Reproduce:**
1. 
2. 
3. 

**Browser:** [Chrome/Firefox/Safari]
**Version:** [Version number]
**OS:** [Windows/Mac/Linux]
**Console Errors:** [Any JavaScript errors]
**Screenshots:** [If applicable]
```

## Post-Testing Actions

### If All Tests Pass
- [ ] Document test results
- [ ] Update other Program Studi pages
- [ ] Train content administrators
- [ ] Monitor for user reports

### If Tests Fail
- [ ] Document failures
- [ ] Review implementation
- [ ] Fix issues
- [ ] Retest

## Sign-Off

### Tester Information
- **Name:** _________________
- **Date:** _________________
- **Role:** _________________

### Test Results
- **Total Tests:** _____
- **Passed:** _____
- **Failed:** _____
- **Skipped:** _____

### Overall Status
- [ ] ✅ All tests passed - Ready for production
- [ ] ⚠️ Minor issues found - Can deploy with notes
- [ ] ❌ Major issues found - Not ready for production

### Notes
```
[Additional observations, recommendations, or concerns]
```

### Approval
- [ ] Technical review complete
- [ ] Content review complete
- [ ] Translation quality verified
- [ ] Ready for deployment

**Approved by:** _________________  
**Date:** _________________

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-02
