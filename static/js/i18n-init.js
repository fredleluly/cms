/**
 * i18n-init.js
 * Multi-language support for CMS
 * Supports: Indonesian (id), English (en), Mandarin (zh)
 */

(function () {
  'use strict';

  // Configuration
  const DEFAULT_LANG = 'id';
  const SUPPORTED_LANGS = ['id', 'en', 'zh'];
  const STORAGE_KEY = 'matana_language';
  
  // Locale configuration for date/number formatting
  const LOCALE_MAP = {
    'id': 'id-ID',
    'en': 'en-US',
    'zh': 'zh-CN'
  };

  // i18n Manager
  const i18n = {
    currentLang: DEFAULT_LANG,
    translations: {},
    
    /**
     * Initialize i18n system
     */
    async init() {
      // Get language from localStorage or default
      this.currentLang = this.getSavedLanguage() || DEFAULT_LANG;
      
      // Load translation for current language
      await this.loadTranslation(this.currentLang);
      
      // Apply translations to DOM
      this.applyTranslations();
      
      // Update language selector UI
      this.updateLanguageSelector();
      
      // Update HTML lang attribute
      document.documentElement.setAttribute('lang', this.currentLang);
      
      console.log('i18n initialized with language:', this.currentLang);
    },
    
    /**
     * Get saved language from localStorage
     */
    getSavedLanguage() {
      const saved = localStorage.getItem(STORAGE_KEY);
      return SUPPORTED_LANGS.includes(saved) ? saved : null;
    },
    
    /**
     * Save language preference
     */
    saveLanguage(lang) {
      localStorage.setItem(STORAGE_KEY, lang);
    },
    
    /**
     * Load translation file
     */
    async loadTranslation(lang) {
      try {
        const response = await fetch(`/static/locales/${lang}.json`);
        if (!response.ok) {
          throw new Error(`Failed to load ${lang}.json`);
        }
        this.translations = await response.json();
      } catch (error) {
        console.error('Error loading translation:', error);
        // Fallback to default language if not already trying it
        if (lang !== DEFAULT_LANG) {
          console.log('Falling back to default language:', DEFAULT_LANG);
          await this.loadTranslation(DEFAULT_LANG);
        }
      }
    },
    
    /**
     * Get translation by key path (e.g., "nav.profile")
     */
    t(keyPath, fallback = '') {
      const keys = keyPath.split('.');
      let value = this.translations;
      
      for (const key of keys) {
        if (value && typeof value === 'object' && key in value) {
          value = value[key];
        } else {
          return fallback || keyPath;
        }
      }
      
      return typeof value === 'string' ? value : (fallback || keyPath);
    },
    
    /**
     * Apply translations to DOM elements with data-i18n attribute
     */
    applyTranslations() {
      const elements = document.querySelectorAll('[data-i18n]');
      
      elements.forEach(element => {
        const key = element.getAttribute('data-i18n');
        const translation = this.t(key);
        
        // Check if we should update placeholder, title, or text content
        const attr = element.getAttribute('data-i18n-attr');
        
        if (attr) {
          element.setAttribute(attr, translation);
        } else {
          // Default: update text content
          element.textContent = translation;
        }
      });
    },
    
    /**
     * Switch to a different language
     */
    async switchLanguage(lang) {
      if (!SUPPORTED_LANGS.includes(lang)) {
        console.warn('Unsupported language:', lang);
        return;
      }
      
      if (lang === this.currentLang) {
        return;
      }
      
      this.currentLang = lang;
      this.saveLanguage(lang);
      
      await this.loadTranslation(lang);
      this.applyTranslations();
      this.updateLanguageSelector();
      
      // Update HTML lang attribute
      document.documentElement.setAttribute('lang', lang);
      
      // Dispatch custom event for other scripts to listen
      window.dispatchEvent(new CustomEvent('languageChanged', { 
        detail: { lang } 
      }));
      
      console.log('Language switched to:', lang);
    },
    
    /**
     * Update language selector UI to show current selection
     */
    updateLanguageSelector() {
      const langButtons = document.querySelectorAll('[data-lang-switch]');
      
      langButtons.forEach(button => {
        const lang = button.getAttribute('data-lang-switch');
        if (lang === this.currentLang) {
          button.classList.add('active', 'text-matana-yellow');
          button.classList.remove('text-white');
        } else {
          button.classList.remove('active', 'text-matana-yellow');
          button.classList.add('text-white');
        }
      });
    },
    
    /**
     * Format date according to current locale
     */
    formatDate(date, options = {}) {
      const locale = LOCALE_MAP[this.currentLang] || LOCALE_MAP[DEFAULT_LANG];
      const defaultOptions = {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      };
      
      return new Intl.DateTimeFormat(locale, { ...defaultOptions, ...options }).format(date);
    },
    
    /**
     * Format number according to current locale
     */
    formatNumber(number, options = {}) {
      const locale = LOCALE_MAP[this.currentLang] || LOCALE_MAP[DEFAULT_LANG];
      return new Intl.NumberFormat(locale, options).format(number);
    },
    
    /**
     * Format currency according to current locale
     */
    formatCurrency(amount, currency = 'IDR', options = {}) {
      const locale = LOCALE_MAP[this.currentLang] || LOCALE_MAP[DEFAULT_LANG];
      const defaultOptions = {
        style: 'currency',
        currency: currency
      };
      
      return new Intl.NumberFormat(locale, { ...defaultOptions, ...options }).format(amount);
    }
  };

  // Make i18n globally available
  window.i18n = i18n;

  // Auto-initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => i18n.init());
  } else {
    i18n.init();
  }

  // Add click handlers for language switcher buttons
  document.addEventListener('click', (e) => {
    const langButton = e.target.closest('[data-lang-switch]');
    if (langButton) {
      e.preventDefault();
      const lang = langButton.getAttribute('data-lang-switch');
      i18n.switchLanguage(lang);
    }
  });

})();
