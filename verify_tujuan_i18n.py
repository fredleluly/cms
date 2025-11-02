#!/usr/bin/env python3
"""
Verification script for tujuan_section internationalization
This script validates that all tujuan_section blocks are properly formatted
"""

import re
import json

def verify_tujuan_sections():
    """Verify all tujuan_section blocks in views.py"""
    
    print("=" * 70)
    print("TUJUAN SECTION INTERNATIONALIZATION VERIFICATION")
    print("=" * 70)
    print()
    
    # Read the file
    with open('/home/runner/work/cms/cms/apps/pages/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all tujuan_section blocks
    pattern = r"'identifier':\s*'tujuan_section',\s*'title':\s*\{[^}]+\},\s*'description':\s*\{[^}]+\},"
    matches = list(re.finditer(pattern, content, re.DOTALL))
    
    print(f"Found {len(matches)} tujuan_section blocks\n")
    
    # Validate each block
    all_valid = True
    for i, match in enumerate(matches, 1):
        block_text = match.group(0)
        
        # Check for required keys
        has_title_id = "'id': 'Tujuan'" in block_text
        has_title_en = "'en': 'Objectives'" in block_text
        has_title_zh = "'zh': '目标'" in block_text
        
        has_desc_id = re.search(r"'description':\s*\{\s*'id':", block_text)
        has_desc_en = re.search(r"'en':", block_text)
        has_desc_zh = re.search(r"'zh':", block_text)
        
        is_valid = all([
            has_title_id, has_title_en, has_title_zh,
            has_desc_id, has_desc_en, has_desc_zh
        ])
        
        status = "✅" if is_valid else "❌"
        print(f"{status} Block {i}:")
        print(f"   Title multilingual: {has_title_id and has_title_en and has_title_zh}")
        print(f"   Description multilingual: {bool(has_desc_id and has_desc_en and has_desc_zh)}")
        
        if not is_valid:
            all_valid = False
            print(f"   ⚠️  VALIDATION FAILED")
        print()
    
    # Summary
    print("=" * 70)
    if all_valid and len(matches) == 10:
        print("✅ SUCCESS! All 10 tujuan_section blocks are properly internationalized!")
        print()
        print("Structure validated:")
        print("  ✓ All blocks have multilingual title (id, en, zh)")
        print("  ✓ All blocks have multilingual description (id, en, zh)")
        print("  ✓ Format matches expected structure for i18n-content.js")
        print()
        print("Next steps:")
        print("  1. Deploy to staging/test environment")
        print("  2. Test language switching on actual prodi pages")
        print("  3. Verify all translations display correctly")
        print("  4. Check fallback mechanism works")
        return True
    else:
        print(f"❌ VALIDATION FAILED!")
        print(f"   Expected: 10 valid blocks")
        print(f"   Found: {len(matches)} blocks, {sum(1 for i in range(len(matches)) if all_valid)} valid")
        return False

def check_template_compatibility():
    """Check if template has required attributes"""
    print()
    print("=" * 70)
    print("TEMPLATE COMPATIBILITY CHECK")
    print("=" * 70)
    print()
    
    with open('/home/runner/work/cms/cms/templates/pages/prodi.html', 'r', encoding='utf-8') as f:
        template = f.read()
    
    has_title_attr = 'data-i18n-content="tujuan_section.title"' in template
    has_desc_attr = 'data-i18n-html="tujuan_section.description"' in template
    
    print(f"{'✅' if has_title_attr else '❌'} Title has data-i18n-content attribute")
    print(f"{'✅' if has_desc_attr else '❌'} Description has data-i18n-html attribute")
    
    if has_title_attr and has_desc_attr:
        print("\n✅ Template is properly configured for i18n!")
        return True
    else:
        print("\n❌ Template needs data-i18n attributes!")
        return False

def check_javascript_handler():
    """Check if JavaScript handler exists"""
    print()
    print("=" * 70)
    print("JAVASCRIPT HANDLER CHECK")
    print("=" * 70)
    print()
    
    try:
        with open('/home/runner/work/cms/cms/static/js/i18n-content.js', 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        has_get_i18n = 'getI18nContent' in js_content
        has_update_html = 'updateHtmlElement' in js_content
        has_fallback = "'id' in content" in js_content or "content['id']" in js_content
        
        print(f"{'✅' if has_get_i18n else '❌'} getI18nContent function exists")
        print(f"{'✅' if has_update_html else '❌'} updateHtmlElement function exists")
        print(f"{'✅' if has_fallback else '❌'} Fallback to Indonesian implemented")
        
        if has_get_i18n and has_update_html and has_fallback:
            print("\n✅ JavaScript handler is properly configured!")
            return True
        else:
            print("\n❌ JavaScript handler may be missing functionality!")
            return False
    except FileNotFoundError:
        print("❌ i18n-content.js not found!")
        return False

if __name__ == '__main__':
    result1 = verify_tujuan_sections()
    result2 = check_template_compatibility()
    result3 = check_javascript_handler()
    
    print()
    print("=" * 70)
    print("FINAL VERIFICATION RESULT")
    print("=" * 70)
    
    if all([result1, result2, result3]):
        print("✅ ALL CHECKS PASSED!")
        print()
        print("The internationalization implementation is complete and ready for testing.")
        print("All tujuan_section blocks are properly configured for multilingual support.")
        exit(0)
    else:
        print("❌ SOME CHECKS FAILED!")
        print()
        print("Please review the issues above before proceeding.")
        exit(1)
