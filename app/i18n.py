import json
import os
from pathlib import Path
from flask import session

class I18n:
    def __init__(self, app=None):
        self.translations = {}
        self.default_language = 'fr'
        self.locales_path = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        self.locales_path = Path(app.root_path) / 'locales'
        self.load_all_languages()
        
    def load_all_languages(self):
        """Scan and load all JSON language files from locales directory"""
        if not self.locales_path or not self.locales_path.exists():
            return
        
        for file_path in self.locales_path.glob('*.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    lang_code = data.get('language_code')
                    if lang_code:
                        self.translations[lang_code] = data
            except Exception as e:
                print(f"Error loading language file {file_path}: {e}")
    
    def get_available_languages(self):
        """Get list of available languages"""
        return [
            {
                'code': code,
                'name': data.get('language_name', code)
            }
            for code, data in self.translations.items()
        ]
    
    def get_current_language(self):
        """Get current language from session"""
        return session.get('language', self.default_language)
    
    def set_language(self, lang_code):
        """Set current language in session"""
        if lang_code in self.translations:
            session['language'] = lang_code
            return True
        return False
    
    def get_translations(self, lang_code=None):
        """Get all translations for a language"""
        if lang_code is None:
            lang_code = self.get_current_language()
        return self.translations.get(lang_code, self.translations.get(self.default_language, {}))
    
    def add_language(self, file_path):
        """Add a new language from uploaded JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            lang_code = data.get('language_code')
            if not lang_code:
                return False, "Missing 'language_code' in JSON file"
            
            # Save to locales directory
            if not self.locales_path:
                return False, "Locales path not initialized"
            dest_path = self.locales_path / f"{lang_code}.json"
            with open(dest_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Load into memory
            self.translations[lang_code] = data
            
            return True, f"Language '{lang_code}' added successfully"
        except json.JSONDecodeError:
            return False, "Invalid JSON format"
        except Exception as e:
            return False, str(e)

i18n = I18n()
