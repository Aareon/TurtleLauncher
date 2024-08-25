import json
from pathlib import Path
from loguru import logger
from turtlelauncher.utils.globals import LOCALES

class Locale:
    def __init__(self, config):
        self.config = config
        self.translations = {}
        self.available_languages = []
        self.load_translations()

    def load_translations(self):
        locale_file = LOCALES / "locales.json"
        try:
            with open(locale_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
            self.available_languages = list(self.translations.keys())
            logger.info(f"Loaded translations for languages: {', '.join(self.available_languages)}")
        except Exception as e:
            logger.error(f"Error loading translations: {str(e)}")
            self.translations = {}
            self.available_languages = []

    def get_translation(self, key, language=None):
        if not language:
            language = self.config.language
        
        if language not in self.translations:
            logger.warning(f"Language '{language}' not found in translations, falling back to English")
            language = 'English'
        
        if key not in self.translations[language]:
            logger.warning(f"Translation key '{key}' not found for language '{language}', falling back to English")
            return self.translations.get('en', {}).get(key, key)
        
        return self.translations[language][key]

    def set_language(self, language):
        if language in self.available_languages:
            self.config.language = language
            self.config.save()
            logger.info(f"Language set to: {language}")
        else:
            logger.warning(f"Attempted to set unsupported language: {language}")

    def get_available_languages(self):
        return self.available_languages

locale_instance = None

def initialize_locale(config):
    global locale_instance
    locale_instance = Locale(config)
    return locale_instance

def get_locale():
    global locale_instance
    if locale_instance is None:
        raise RuntimeError("Locale has not been initialized. Call initialize_locale first.")
    return locale_instance