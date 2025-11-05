/**
 * i18n-blocks.js
 * Runtime translation support for content blocks with embedded translations
 * Works with profile.html, prodi.html, and mitra.html templates
 */

(function() {
    'use strict';

    /**
     * Apply block translations based on current language
     * Looks for elements with data-block-html-id, data-block-html-en, data-block-html-zh
     * and swaps innerHTML based on current language
     */
    function applyBlockTranslations() {
        // Get current language from i18n system or localStorage
        let currentLang = 'id'; // default
        
        if (window.i18n && window.i18n.getCurrentLanguage) {
            currentLang = window.i18n.getCurrentLanguage();
        } else if (typeof localStorage !== 'undefined') {
            currentLang = localStorage.getItem('matana_language') || 'id';
        }

        console.log(`[i18n-blocks] Applying block translations for language: ${currentLang}`);

        // Find all elements with block translation data attributes
        const elements = document.querySelectorAll('[data-block-html-id]');
        
        elements.forEach(element => {
            const attrName = `data-block-html-${currentLang}`;
            const translatedContent = element.getAttribute(attrName);
            
            if (translatedContent) {
                // Decode HTML entities and set innerHTML
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = translatedContent;
                element.innerHTML = tempDiv.innerHTML;
            } else {
                // Fallback to Indonesian if requested language not available
                const fallbackContent = element.getAttribute('data-block-html-id');
                if (fallbackContent && currentLang !== 'id') {
                    console.warn(`[i18n-blocks] No translation found for ${currentLang}, using Indonesian`);
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML = fallbackContent;
                    element.innerHTML = tempDiv.innerHTML;
                }
            }
        });

        // After updating block translations, also update standard i18n elements
        if (window.i18n && window.i18n.updateDOM) {
            window.i18n.updateDOM();
        }
    }

    /**
     * Initialize block translations on page load
     */
    function initBlockTranslations() {
        console.log('[i18n-blocks] Initializing block translations');
        
        // Apply translations on initial load
        applyBlockTranslations();

        // Listen for language change events
        window.addEventListener('languageChanged', function(event) {
            console.log('[i18n-blocks] Language changed, updating blocks');
            applyBlockTranslations();
        });

        console.log('[i18n-blocks] Initialization complete');
    }

    // Expose applyBlockTranslations globally for manual triggering
    window.applyBlockTranslations = applyBlockTranslations;

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initBlockTranslations);
    } else {
        // DOM already loaded
        initBlockTranslations();
    }

})();
