/**
 * i18n-content.js
 * Handles dynamic multilingual content switching for Program Studi pages
 * Works in conjunction with i18n-init.js for complete internationalization
 */

(function() {
    'use strict';

    /**
     * Get nested value from object using dot notation
     * e.g., getNestedValue(obj, 'hero_section.title.en')
     */
    function getNestedValue(obj, path) {
        if (!obj || !path) return null;
        
        const keys = path.split('.');
        let value = obj;
        
        for (const key of keys) {
            if (value && typeof value === 'object' && key in value) {
                value = value[key];
            } else {
                return null;
            }
        }
        
        return value;
    }

    /**
     * Get language-specific content from multilingual object
     * Supports both direct language keys and nested structures
     */
    function getI18nContent(content, language = 'id') {
        if (!content) return '';
        
        // If it's already a string, return it
        if (typeof content === 'string') {
            return content;
        }
        
        // If it's an object with language keys
        if (typeof content === 'object') {
            // Try requested language
            if (language in content) {
                return content[language];
            }
            // Fallback to Indonesian
            if ('id' in content) {
                return content['id'];
            }
            // Fallback to first available language
            const supportedLangs = ['id', 'en', 'zh'];
            for (const lang of supportedLangs) {
                if (lang in content) {
                    return content[lang];
                }
            }
        }
        
        return content;
    }

    /**
     * Update element content based on data-i18n-content attribute
     */
    function updateContentElement(element, language) {
        const contentPath = element.getAttribute('data-i18n-content');
        if (!contentPath) return;

        // Get content from window.pageBlocks
        if (!window.pageBlocks) {
            console.warn('window.pageBlocks is not defined');
            return;
        }

        const content = getNestedValue(window.pageBlocks, contentPath);
        if (!content) {
            console.warn(`Content not found for path: ${contentPath}`);
            return;
        }

        const translatedContent = getI18nContent(content, language);
        
        // Update element based on its type
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            element.value = translatedContent;
        } else {
            element.textContent = translatedContent;
        }
    }

    /**
     * Update element HTML content based on data-i18n-html attribute
     */
    function updateHtmlElement(element, language) {
        const contentPath = element.getAttribute('data-i18n-html');
        if (!contentPath) return;

        if (!window.pageBlocks) {
            console.warn('window.pageBlocks is not defined');
            return;
        }

        const content = getNestedValue(window.pageBlocks, contentPath);
        if (!content) {
            console.warn(`Content not found for path: ${contentPath}`);
            return;
        }

        const translatedContent = getI18nContent(content, language);
        element.innerHTML = translatedContent;
    }

    /**
     * Update mission items (special case for newline-separated missions)
     */
    function updateMissionItems(language) {
        const missionsContainer = document.getElementById('missions-container');
        if (!missionsContainer || !window.pageBlocks) return;

        // Get mission description
        const missionContent = getNestedValue(window.pageBlocks, 'visi_misi_section.items.1.description');
        if (!missionContent) return;

        const missionText = getI18nContent(missionContent, language);
        if (!missionText) return;

        // Split by newlines to get individual missions
        const missions = missionText.split('\n').filter(m => m.trim());

        // Update existing mission elements
        const missionElements = missionsContainer.querySelectorAll('.mission-text');
        missionElements.forEach((element, index) => {
            if (index < missions.length) {
                element.textContent = missions[index];
            }
        });
    }

    /**
     * Update konsentrasi items
     */
    function updateKonsentrasiItems(language) {
        const container = document.getElementById('konsentrasi-items');
        if (!container || !window.pageBlocks) return;

        const items = window.pageBlocks.konsentrasi_section?.items;
        if (!items || !Array.isArray(items)) return;

        const itemElements = container.querySelectorAll('[data-i18n-content^="konsentrasi_section.items"]');
        itemElements.forEach((element) => {
            updateContentElement(element, language);
        });
    }

    /**
     * Update kurikulum items
     */
    function updateKurikulumItems(language) {
        const container = document.getElementById('kurikulum-items');
        if (!container || !window.pageBlocks) return;

        const items = window.pageBlocks.kurikulum_section?.items;
        if (!items || !Array.isArray(items)) return;

        const itemElements = container.querySelectorAll('[data-i18n-content^="kurikulum_section.items"]');
        itemElements.forEach((element) => {
            updateContentElement(element, language);
        });
    }

    /**
     * Update karir items
     */
    function updateKarirItems(language) {
        const container = document.getElementById('karir-items');
        if (!container || !window.pageBlocks) return;

        const items = window.pageBlocks.peluang_karir_section?.items;
        if (!items || !Array.isArray(items)) return;

        const itemElements = container.querySelectorAll('[data-i18n-content^="peluang_karir_section.items"]');
        itemElements.forEach((element) => {
            updateContentElement(element, language);
        });
    }

    /**
     * Update all dynamic content on the page
     */
    function updateAllContent(language) {
        console.log(`Updating dynamic content to language: ${language}`);

        // Update all elements with data-i18n-content
        const contentElements = document.querySelectorAll('[data-i18n-content]');
        contentElements.forEach(element => {
            updateContentElement(element, language);
        });

        // Update all elements with data-i18n-html
        const htmlElements = document.querySelectorAll('[data-i18n-html]');
        htmlElements.forEach(element => {
            updateHtmlElement(element, language);
        });

        // Update special sections
        updateMissionItems(language);
        updateKonsentrasiItems(language);
        updateKurikulumItems(language);
        updateKarirItems(language);
    }

    /**
     * Initialize content internationalization
     */
    function initContentI18n() {
        // Listen for language change events from i18n-init.js
        window.addEventListener('languageChanged', (event) => {
            const newLanguage = event.detail.language;
            updateAllContent(newLanguage);
        });

        // Initial update with current language
        if (window.i18n && window.i18n.getCurrentLanguage) {
            const currentLanguage = window.i18n.getCurrentLanguage();
            updateAllContent(currentLanguage);
        }

        console.log('i18n-content.js initialized');
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initContentI18n);
    } else {
        initContentI18n();
    }

})();
