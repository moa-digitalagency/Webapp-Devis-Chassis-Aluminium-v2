// I18n Client-side Manager
class I18nManager {
    constructor() {
        this.currentLanguage = 'fr';
        this.translations = {};
        this.availableLanguages = [];
        this.init();
    }

    async init() {
        await this.loadAvailableLanguages();
        await this.loadCurrentLanguage();
    }

    async loadAvailableLanguages() {
        try {
            const response = await fetch('/api/languages/available');
            if (response.ok) {
                this.availableLanguages = await response.json();
            }
        } catch (error) {
            console.error('Error loading available languages:', error);
        }
    }

    async loadCurrentLanguage() {
        try {
            const response = await fetch('/api/languages/current');
            if (response.ok) {
                const data = await response.json();
                this.currentLanguage = data.code;
                this.translations = data.translations;
                this.updatePage();
            }
        } catch (error) {
            console.error('Error loading current language:', error);
        }
    }

    async setLanguage(langCode) {
        try {
            const response = await fetch('/api/languages/set', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ language: langCode })
            });

            if (response.ok) {
                await this.loadCurrentLanguage();
                return true;
            }
        } catch (error) {
            console.error('Error setting language:', error);
        }
        return false;
    }

    t(key) {
        const keys = key.split('.');
        let value = this.translations;
        
        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = value[k];
            } else {
                return key;
            }
        }
        
        return value || key;
    }

    updatePage() {
        // Update all elements with data-i18n attribute
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.t(key);
            
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.placeholder = translation;
            } else {
                element.textContent = translation;
            }
        });

        // Update all elements with data-i18n-title attribute
        document.querySelectorAll('[data-i18n-title]').forEach(element => {
            const key = element.getAttribute('data-i18n-title');
            element.title = this.t(key);
        });
    }

    createLanguageSwitcher() {
        const switcher = document.createElement('div');
        switcher.className = 'language-switcher';
        switcher.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 8px;
        `;

        const select = document.createElement('select');
        select.className = 'form-control';
        select.style.cssText = `
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 14px;
            cursor: pointer;
        `;

        this.availableLanguages.forEach(lang => {
            const option = document.createElement('option');
            option.value = lang.code;
            option.textContent = lang.name;
            option.selected = lang.code === this.currentLanguage;
            select.appendChild(option);
        });

        select.addEventListener('change', async (e) => {
            const success = await this.setLanguage(e.target.value);
            if (success) {
                location.reload();
            }
        });

        switcher.appendChild(select);
        return switcher;
    }

    async uploadLanguageFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/languages/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (response.ok) {
                await this.loadAvailableLanguages();
                return { success: true, message: data.message };
            } else {
                return { success: false, error: data.error };
            }
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
}

// Global instance
const i18n = new I18nManager();

// Add language switcher to page when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Only add switcher on admin pages (not login)
    if (!window.location.pathname.includes('login')) {
        const switcher = i18n.createLanguageSwitcher();
        document.body.appendChild(switcher);
    }
});
