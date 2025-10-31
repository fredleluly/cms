"""
Test i18n functionality
"""
import json
import os
from django.test import TestCase, Client
from django.conf import settings


class I18nTestCase(TestCase):
    """Test cases for i18n implementation"""
    
    def setUp(self):
        """Set up test client"""
        self.client = Client()
    
    def test_locale_files_exist(self):
        """Test that all locale files exist"""
        locales_path = os.path.join(settings.BASE_DIR, 'static', 'locales')
        
        # Check if locales directory exists
        self.assertTrue(os.path.exists(locales_path), 
                       f"Locales directory not found at {locales_path}")
        
        # Check if all required locale files exist
        for lang in ['id', 'en', 'zh']:
            locale_file = os.path.join(locales_path, f'{lang}.json')
            self.assertTrue(os.path.exists(locale_file), 
                           f"Locale file {lang}.json not found")
    
    def test_locale_files_valid_json(self):
        """Test that all locale files are valid JSON"""
        locales_path = os.path.join(settings.BASE_DIR, 'static', 'locales')
        
        for lang in ['id', 'en', 'zh']:
            locale_file = os.path.join(locales_path, f'{lang}.json')
            with open(locale_file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    self.assertIsInstance(data, dict, 
                                        f"{lang}.json is not a valid JSON object")
                except json.JSONDecodeError as e:
                    self.fail(f"{lang}.json contains invalid JSON: {e}")
    
    def test_locale_files_have_required_keys(self):
        """Test that all locale files have required translation keys"""
        locales_path = os.path.join(settings.BASE_DIR, 'static', 'locales')
        required_top_level_keys = ['nav', 'common', 'footer']
        
        for lang in ['id', 'en', 'zh']:
            locale_file = os.path.join(locales_path, f'{lang}.json')
            with open(locale_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                for key in required_top_level_keys:
                    self.assertIn(key, data, 
                                f"{lang}.json missing required key: {key}")
    
    def test_i18n_init_js_exists(self):
        """Test that i18n-init.js exists"""
        i18n_file = os.path.join(settings.BASE_DIR, 'static', 'js', 'i18n-init.js')
        self.assertTrue(os.path.exists(i18n_file), 
                       f"i18n-init.js not found at {i18n_file}")
    
    def test_locale_files_consistency(self):
        """Test that all locale files have the same structure"""
        locales_path = os.path.join(settings.BASE_DIR, 'static', 'locales')
        
        # Load all locale files
        locales = {}
        for lang in ['id', 'en', 'zh']:
            locale_file = os.path.join(locales_path, f'{lang}.json')
            with open(locale_file, 'r', encoding='utf-8') as f:
                locales[lang] = json.load(f)
        
        # Get keys from Indonesian (default) locale
        def get_all_keys(d, prefix=''):
            keys = set()
            for k, v in d.items():
                key_path = f"{prefix}.{k}" if prefix else k
                keys.add(key_path)
                if isinstance(v, dict):
                    keys.update(get_all_keys(v, key_path))
            return keys
        
        id_keys = get_all_keys(locales['id'])
        
        # Compare with other locales
        for lang in ['en', 'zh']:
            lang_keys = get_all_keys(locales[lang])
            
            # Check for missing keys
            missing = id_keys - lang_keys
            if missing:
                self.fail(f"{lang}.json is missing keys: {missing}")
            
            # Check for extra keys
            extra = lang_keys - id_keys
            if extra:
                self.fail(f"{lang}.json has extra keys: {extra}")
