/**
 * i18n-init.js
 * Simple internationalization (i18n) library for Matana University CMS
 * Supports ID (Bahasa Indonesia), EN (English), and ZH (Mandarin Chinese)
 */

(function() {
    'use strict';

    // Available languages
    const LANGUAGES = {
        'id': { name: 'Bahasa Indonesia', flag: '🇮🇩' },
        'en': { name: 'English', flag: '🇬🇧' },
        'zh': { name: '中文', flag: '🇨🇳' }
    };

    // Default language
    const DEFAULT_LANGUAGE = 'id';

    // Storage key for language preference
    const STORAGE_KEY = 'matana_language';

    // Cache for loaded translations
    const translationsCache = {};

    /**
     * I18n class for managing internationalization
     */
    class I18n {
        constructor() {
            this.currentLanguage = this.getStoredLanguage() || DEFAULT_LANGUAGE;
            this.translations = {};
            this.initialized = false;
        }

        /**
         * Get stored language from localStorage
         */
        getStoredLanguage() {
            try {
                return localStorage.getItem(STORAGE_KEY);
            } catch (e) {
                console.warn('localStorage not available:', e);
                return null;
            }
        }

        /**
         * Store language preference in localStorage
         */
        setStoredLanguage(lang) {
            try {
                localStorage.setItem(STORAGE_KEY, lang);
            } catch (e) {
                console.warn('Could not store language preference:', e);
            }
        }

        /**
         * Load translations for a specific language
         */
        async loadTranslations(lang) {
            // Return cached translations if available
            if (translationsCache[lang]) {
                return translationsCache[lang];
            }

            try {
                // Dynamically determine the base path
                const basePath = window.location.origin;
                const response = await fetch(`${basePath}/static/locales/${lang}.json`);
                
                if (!response.ok) {
                    throw new Error(`Failed to load translations for ${lang}`);
                }
                
                const translations = await response.json();
                translationsCache[lang] = translations;
                return translations;
            } catch (error) {
                console.error(`Error loading translations for ${lang}:`, error);
                
                // Fallback to default language if not already trying it
                if (lang !== DEFAULT_LANGUAGE) {
                    console.warn(`Falling back to ${DEFAULT_LANGUAGE}`);
                    return this.loadTranslations(DEFAULT_LANGUAGE);
                }
                
                return {};
            }
        }

        /**
         * Initialize i18n
         */
        async init(lang = null) {
            const targetLang = lang || this.currentLanguage;
            
            try {
                this.translations = await this.loadTranslations(targetLang);
                this.currentLanguage = targetLang;
                this.setStoredLanguage(targetLang);
                this.updateDOM();
                this.updateHTMLLang();
                this.initialized = true;
                
                // Dispatch event to notify that language has changed
                window.dispatchEvent(new CustomEvent('languageChanged', { 
                    detail: { language: targetLang } 
                }));
                
                console.log(`Language initialized: ${targetLang}`);
            } catch (error) {
                console.error('Error initializing i18n:', error);
            }
        }

        /**
         * Get translation by key path (e.g., 'nav.profile')
         */
        t(keyPath) {
            const keys = keyPath.split('.');
            let value = this.translations;
            
            for (const key of keys) {
                if (value && typeof value === 'object' && key in value) {
                    value = value[key];
                } else {
                    console.warn(`Translation key not found: ${keyPath}`);
                    return keyPath; // Return key path if translation not found
                }
            }
            
            return value;
        }

        /**
         * Update all elements with data-i18n attribute
         */
        updateDOM() {
            const elements = document.querySelectorAll('[data-i18n]');
            
            elements.forEach(element => {
                const key = element.getAttribute('data-i18n');
                const translation = this.t(key);
                
                // Update text content or specific attribute
                const attr = element.getAttribute('data-i18n-attr');
                if (attr) {
                    element.setAttribute(attr, translation);
                } else {
                    element.textContent = translation;
                }
            });
        }

        /**
         * Update HTML lang attribute
         */
        updateHTMLLang() {
            document.documentElement.setAttribute('lang', this.currentLanguage);
        }

        /**
         * Change language
         */
        async changeLanguage(lang) {
            if (!LANGUAGES[lang]) {
                console.error(`Invalid language: ${lang}`);
                return;
            }

            if (lang === this.currentLanguage) {
                console.log(`Already using language: ${lang}`);
                return;
            }

            await this.init(lang);
        }

        /**
         * Get current language
         */
        getCurrentLanguage() {
            return this.currentLanguage;
        }

        /**
         * Get available languages
         */
        getAvailableLanguages() {
            return LANGUAGES;
        }
    }

    // Create global i18n instance
    window.i18n = new I18n();

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.i18n.init();
        });
    } else {
        window.i18n.init();
    }

    // Language switcher utility functions
    window.switchLanguage = function(lang) {
        window.i18n.changeLanguage(lang);
    };

    window.getCurrentLanguage = function() {
        return window.i18n.getCurrentLanguage();
    };

    window.getAvailableLanguages = function() {
        return window.i18n.getAvailableLanguages();
    };

})();
