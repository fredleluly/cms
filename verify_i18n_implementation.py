#!/usr/bin/env python3
"""
Verification script for Program Studi i18n implementation
Checks if all required components are in place
"""

import os
import json
from pathlib import Path

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def check_file_exists(filepath, description):
    """Check if a file exists and print result"""
    if os.path.exists(filepath):
        print(f"{GREEN}✓{RESET} {description}: {filepath}")
        return True
    else:
        print(f"{RED}✗{RESET} {description}: {filepath} NOT FOUND")
        return False

def check_json_valid(filepath):
    """Check if JSON file is valid"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            json.load(f)
        print(f"  {GREEN}✓{RESET} Valid JSON")
        return True
    except json.JSONDecodeError as e:
        print(f"  {RED}✗{RESET} Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"  {RED}✗{RESET} Error: {e}")
        return False

def check_locale_keys_consistency():
    """Check if all locale files have consistent keys"""
    locales = {}
    files = {
        'id': 'static/locales/id.json',
        'en': 'static/locales/en.json',
        'zh': 'static/locales/zh.json'
    }
    
    for lang, filepath in files.items():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                locales[lang] = json.load(f)
        except:
            print(f"{RED}✗{RESET} Could not load {filepath}")
            return False
    
    # Check prodi keys
    prodi_keys = {}
    for lang, data in locales.items():
        prodi_keys[lang] = set(data.get('prodi', {}).keys())
    
    id_keys = prodi_keys['id']
    en_keys = prodi_keys['en']
    zh_keys = prodi_keys['zh']
    
    if id_keys == en_keys == zh_keys:
        print(f"{GREEN}✓{RESET} All prodi keys are consistent across all languages ({len(id_keys)} keys)")
        return True
    else:
        print(f"{RED}✗{RESET} Prodi keys are inconsistent:")
        missing_in_en = id_keys - en_keys
        missing_in_zh = id_keys - zh_keys
        if missing_in_en:
            print(f"  Missing in EN: {missing_in_en}")
        if missing_in_zh:
            print(f"  Missing in ZH: {missing_in_zh}")
        return False

def check_template_i18n_attributes():
    """Check if template has proper i18n attributes"""
    template_path = 'templates/pages/prodi.html'
    
    if not os.path.exists(template_path):
        print(f"{RED}✗{RESET} Template not found: {template_path}")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for data-i18n attributes
    has_data_i18n = 'data-i18n=' in content
    has_data_i18n_content = 'data-i18n-content=' in content
    has_data_i18n_html = 'data-i18n-html=' in content
    
    if has_data_i18n:
        print(f"{GREEN}✓{RESET} Template has data-i18n attributes (static UI)")
    else:
        print(f"{YELLOW}⚠{RESET} Template may be missing data-i18n attributes")
    
    if has_data_i18n_content:
        print(f"{GREEN}✓{RESET} Template has data-i18n-content attributes (dynamic content)")
    else:
        print(f"{RED}✗{RESET} Template is missing data-i18n-content attributes")
        return False
    
    if has_data_i18n_html:
        print(f"{GREEN}✓{RESET} Template has data-i18n-html attributes (rich content)")
    else:
        print(f"{YELLOW}⚠{RESET} Template may not have data-i18n-html attributes")
    
    # Check if i18n-content.js is loaded
    if 'i18n-content.js' in content:
        print(f"{GREEN}✓{RESET} Template loads i18n-content.js")
    else:
        print(f"{RED}✗{RESET} Template does not load i18n-content.js")
        return False
    
    return True

def main():
    """Main verification function"""
    print("\n" + "="*60)
    print("Program Studi i18n Implementation Verification")
    print("="*60 + "\n")
    
    results = []
    
    # Check 1: Core JavaScript files
    print("1. Checking JavaScript files...")
    results.append(check_file_exists('static/js/i18n-init.js', 'i18n-init.js'))
    results.append(check_file_exists('static/js/i18n-content.js', 'i18n-content.js'))
    print()
    
    # Check 2: Locale files
    print("2. Checking locale files...")
    for lang in ['id', 'en', 'zh']:
        filepath = f'static/locales/{lang}.json'
        if check_file_exists(filepath, f'{lang.upper()} locale'):
            check_json_valid(filepath)
    print()
    
    # Check 3: Locale keys consistency
    print("3. Checking locale keys consistency...")
    results.append(check_locale_keys_consistency())
    print()
    
    # Check 4: Template filters
    print("4. Checking template filters...")
    results.append(check_file_exists('apps/pages/templatetags/i18n_filters.py', 'i18n_filters.py'))
    print()
    
    # Check 5: Template
    print("5. Checking template...")
    results.append(check_template_i18n_attributes())
    print()
    
    # Check 6: Documentation
    print("6. Checking documentation...")
    results.append(check_file_exists('DOKUMENTASI_PENAMBAHAN_TERJEMAHAN.md', 'Indonesian documentation'))
    results.append(check_file_exists('ADMIN_MULTILINGUAL_GUIDE.md', 'Admin guide'))
    results.append(check_file_exists('MULTILINGUAL_CONTENT_GUIDE.md', 'Developer guide'))
    results.append(check_file_exists('I18N_PRODI_IMPLEMENTATION.md', 'Implementation summary'))
    print()
    
    # Check 7: Helper scripts
    print("7. Checking helper scripts...")
    results.append(check_file_exists('migrate_prodi_content.py', 'Migration script'))
    results.append(check_file_exists('example_prodi_content_multilingual.json', 'Example content'))
    results.append(check_file_exists('check_i18n_keys.py', 'Key checker script'))
    print()
    
    # Summary
    print("="*60)
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    print(f"\nResults: {passed}/{total} checks passed")
    
    if failed == 0:
        print(f"{GREEN}✓ All checks passed! i18n implementation is complete.{RESET}")
        return 0
    else:
        print(f"{RED}✗ {failed} check(s) failed. Please review the issues above.{RESET}")
        return 1

if __name__ == '__main__':
    exit(main())
