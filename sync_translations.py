#!/usr/bin/env python3
"""
Sync translation files from /locales/ to /static/locales/
Run this after editing translation files to ensure they're served to the browser.
"""

import shutil
import os
import sys

def sync_translations():
    """Copy translation files from locales/ to static/locales/"""
    
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = script_dir
    
    src_dir = os.path.join(project_root, 'locales')
    dst_dir = os.path.join(project_root, 'static', 'locales')
    
    # Ensure destination directory exists
    os.makedirs(dst_dir, exist_ok=True)
    
    # Files to sync
    files = ['id.json', 'en.json', 'zh.json']
    
    print("Syncing translation files...")
    print(f"From: {src_dir}")
    print(f"To: {dst_dir}")
    print("-" * 50)
    
    success_count = 0
    error_count = 0
    
    for file in files:
        src_path = os.path.join(src_dir, file)
        dst_path = os.path.join(dst_dir, file)
        
        try:
            if not os.path.exists(src_path):
                print(f"⚠️  {file}: Source file not found")
                error_count += 1
                continue
            
            shutil.copy2(src_path, dst_path)
            print(f"✅ {file}: Synced successfully")
            success_count += 1
            
        except Exception as e:
            print(f"❌ {file}: Error - {e}")
            error_count += 1
    
    print("-" * 50)
    print(f"Sync complete: {success_count} succeeded, {error_count} failed")
    
    return error_count == 0

if __name__ == '__main__':
    success = sync_translations()
    sys.exit(0 if success else 1)
