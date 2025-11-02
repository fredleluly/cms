#!/usr/bin/env python3
"""
Content Migration Script for Multilingual Support
This script converts existing single-language ContentBlock data to multilingual format.

Usage:
    python3 migrate_prodi_content.py [--dry-run] [--program-slug SLUG]
    
Options:
    --dry-run           Show what would be changed without making changes
    --program-slug      Only migrate content for specific program (e.g., prodi-informatika)
    --help              Show this help message

Example:
    # Dry run to see what would change
    python3 migrate_prodi_content.py --dry-run
    
    # Migrate specific program
    python3 migrate_prodi_content.py --program-slug prodi-informatika
    
    # Migrate all prodi pages
    python3 migrate_prodi_content.py
"""

import os
import sys
import django
import argparse
import json
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from apps.pages.models import Page, ContentBlock

# Configuration
TRANSLATION_PREFIXES = {
    'en': '[EN_TODO]',
    'zh': '[ZH_TODO]'
}

# Fields that should not be translated (images, URLs, etc.)
# Can be extended to include pattern matching
NON_TRANSLATABLE_FIELDS = {'image', 'background_image', 'url', 'icon', 'cta', 'link', 'href'}


def is_multilingual(value):
    """Check if a value is already in multilingual format"""
    if not isinstance(value, dict):
        return False
    return any(key in value for key in ['id', 'en', 'zh'])


def should_skip_field(field_name):
    """
    Determine if a field should be skipped for translation.
    Checks both exact matches and patterns (e.g., fields ending with _image or _url)
    """
    if field_name in NON_TRANSLATABLE_FIELDS:
        return True
    # Check for common patterns
    skip_patterns = ['_image', '_url', '_link', '_icon', '_href']
    return any(field_name.endswith(pattern) for pattern in skip_patterns)


def convert_to_multilingual(value, field_name=''):
    """
    Convert a single-language value to multilingual format.
    
    Args:
        value: The value to convert (string, dict, list, etc.)
        field_name: Name of the field (used to check if it should be skipped)
        
    Returns:
        Multilingual version of the value
    """
    if value is None:
        return None
    
    # Already multilingual
    if isinstance(value, dict) and is_multilingual(value):
        return value
    
    # String value - convert to multilingual
    if isinstance(value, str):
        return {
            'id': value,
            'en': f"{TRANSLATION_PREFIXES['en']} {value}",
            'zh': f"{TRANSLATION_PREFIXES['zh']} {value}"
        }
    
    # List - convert each item
    if isinstance(value, list):
        return [convert_to_multilingual(item, field_name) for item in value]
    
    # Dict - recursively convert values (but skip image/url fields)
    if isinstance(value, dict):
        result = {}
        for key, val in value.items():
            if should_skip_field(key):
                result[key] = val  # Keep as-is
            else:
                result[key] = convert_to_multilingual(val, key)
        return result
    
    # Other types - return as-is
    return value


def migrate_content_block(block, dry_run=False):
    """
    Migrate a single content block to multilingual format.
    
    Args:
        block: ContentBlock instance
        dry_run: If True, show changes without saving
        
    Returns:
        Tuple of (changed, old_content, new_content)
    """
    old_content = block.content.copy()
    new_content = {}
    changed = False
    
    # Fields that should be multilingual
    multilingual_fields = ['title', 'subtitle', 'description']
    
    for key, value in old_content.items():
        if key in multilingual_fields or key == 'items':
            new_value = convert_to_multilingual(value, key)
            new_content[key] = new_value
            if new_value != value:
                changed = True
        else:
            new_content[key] = value
    
    if changed and not dry_run:
        block.content = new_content
        block.save()
        print(f"  ✓ Migrated block: {block.identifier}")
    elif changed:
        print(f"  [DRY-RUN] Would migrate block: {block.identifier}")
    
    return changed, old_content, new_content


def migrate_page(page, dry_run=False):
    """
    Migrate all content blocks for a page.
    
    Args:
        page: Page instance
        dry_run: If True, show changes without saving
        
    Returns:
        Number of blocks changed
    """
    print(f"\nProcessing page: {page.title} ({page.slug})")
    blocks_changed = 0
    
    for block in page.content_blocks.all():
        changed, old, new = migrate_content_block(block, dry_run)
        if changed:
            blocks_changed += 1
            
            # Show a sample of changes
            if dry_run and block.identifier in ['hero_section', 'tujuan_section']:
                print(f"\n  Sample change for {block.identifier}:")
                print(f"    Old title: {old.get('title', 'N/A')}")
                print(f"    New title: {new.get('title', 'N/A')}")
    
    return blocks_changed


def main():
    parser = argparse.ArgumentParser(
        description='Migrate Program Studi content to multilingual format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without making changes'
    )
    parser.add_argument(
        '--program-slug',
        help='Only migrate content for specific program (e.g., prodi-informatika)'
    )
    
    args = parser.parse_args()
    
    # Get pages to migrate
    if args.program_slug:
        pages = Page.objects.filter(slug=args.program_slug, template='prodi.html')
        if not pages.exists():
            print(f"Error: No prodi page found with slug '{args.program_slug}'")
            return 1
    else:
        pages = Page.objects.filter(template='prodi.html')
    
    if not pages.exists():
        print("No prodi pages found to migrate.")
        return 0
    
    print(f"Found {pages.count()} prodi page(s) to migrate")
    if args.dry_run:
        print("=" * 60)
        print("DRY RUN MODE - No changes will be saved")
        print("=" * 60)
    
    total_blocks_changed = 0
    
    for page in pages:
        blocks_changed = migrate_page(page, args.dry_run)
        total_blocks_changed += blocks_changed
    
    print("\n" + "=" * 60)
    print(f"Migration {'would affect' if args.dry_run else 'completed'}:")
    print(f"  - {pages.count()} page(s) processed")
    print(f"  - {total_blocks_changed} block(s) {'would be ' if args.dry_run else ''}changed")
    print("=" * 60)
    
    if args.dry_run and total_blocks_changed > 0:
        print("\nTo apply these changes, run without --dry-run flag")
        print("\nIMPORTANT: After migration, you must:")
        print("  1. Review the [TRANSLATE] placeholders")
        print("  2. Replace them with actual translations")
        print("  3. Test language switching on the website")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
