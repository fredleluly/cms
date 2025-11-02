#!/usr/bin/env python3
"""
I18n Key Consistency Checker
Verifies that all locale files (id.json, en.json, zh.json) have the same translation keys.
"""

import json
import sys
from pathlib import Path

def get_all_keys(data, prefix=''):
    """Recursively get all keys from a nested dictionary."""
    keys = set()
    for key, value in data.items():
        current_key = f"{prefix}.{key}" if prefix else key
        keys.add(current_key)
        if isinstance(value, dict):
            keys.update(get_all_keys(value, current_key))
    return keys

def load_locale_file(filepath):
    """Load a locale JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}")
        return None

def main():
    # Define locale file paths
    base_path = Path(__file__).parent / 'static' / 'locales'
    locale_files = {
        'id': base_path / 'id.json',
        'en': base_path / 'en.json',
        'zh': base_path / 'zh.json'
    }
    
    # Load all locale files
    locales = {}
    for lang, filepath in locale_files.items():
        data = load_locale_file(filepath)
        if data is None:
            sys.exit(1)
        locales[lang] = data
    
    # Get keys from each locale
    keys_by_locale = {}
    for lang, data in locales.items():
        keys_by_locale[lang] = get_all_keys(data)
    
    # Find common keys and differences
    all_keys = set()
    for keys in keys_by_locale.values():
        all_keys.update(keys)
    
    print("="*60)
    print("I18n Key Consistency Check")
    print("="*60)
    print()
    
    # Check for missing keys in each locale
    all_consistent = True
    for lang, keys in keys_by_locale.items():
        missing_keys = all_keys - keys
        if missing_keys:
            all_consistent = False
            print(f"❌ Missing keys in {lang}.json:")
            for key in sorted(missing_keys):
                print(f"   - {key}")
            print()
        else:
            print(f"✓ {lang}.json: All keys present ({len(keys)} keys)")
    
    print()
    
    # Check for extra keys (shouldn't happen but let's be thorough)
    for lang, keys in keys_by_locale.items():
        extra_keys = keys - all_keys
        if extra_keys:
            all_consistent = False
            print(f"⚠ Extra keys in {lang}.json (not in all files):")
            for key in sorted(extra_keys):
                print(f"   - {key}")
            print()
    
    # Summary
    print("="*60)
    if all_consistent:
        print("✓ SUCCESS: All locale files have consistent keys!")
        print(f"Total translation keys: {len(all_keys)}")
        print()
        
        # Count keys by section
        sections = {}
        for key in all_keys:
            section = key.split('.')[0]
            sections[section] = sections.get(section, 0) + 1
        
        print("Keys by section:")
        for section, count in sorted(sections.items()):
            print(f"  - {section}: {count} keys")
    else:
        print("❌ FAILED: Locale files have inconsistent keys!")
        print("Please ensure all locale files have the same translation keys.")
        sys.exit(1)
    
    print("="*60)

if __name__ == '__main__':
    main()
