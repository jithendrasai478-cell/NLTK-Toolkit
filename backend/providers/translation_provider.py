from abc import ABC, abstractmethod
from typing import Any, Dict, List
import requests
from backend.utils.error_handlers import APIException

SUPPORTED_LANGUAGES: Dict[str, str] = {
    "en": "English",
    "te": "Telugu (తెలుగు)",
    "hi": "Hindi (हिन्दी)",
    "ta": "Tamil (தமிழ்)",
    "kn": "Kannada (ಕನ್ನಡ)",
    "ml": "Malayalam (മലയാളം)",
    "bn": "Bengali (বাংলা)",
    "mr": "Marathi (मराठी)",
    "ur": "Urdu (اردو)",
    "fr": "French (Français)",
    "es": "Spanish (Español)",
    "de": "German (Deutsch)",
    "ja": "Japanese (日本語)",
    "zh": "Chinese (中文)",
}

class BaseTranslationProvider(ABC):
    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        pass

    @abstractmethod
    def get_supported_languages(self) -> Dict[str, str]:
        pass

class MockTranslationProvider(BaseTranslationProvider):
    """Deterministic offline mock provider for automated tests and standalone environments."""
    
    DICTIONARY: Dict[str, Dict[str, str]] = {
        "hello": {
            "te": "నమస్కారం",
            "hi": "नमस्ते",
            "fr": "Bonjour",
            "es": "Hola",
            "de": "Hallo",
            "ja": "こんにちは",
            "zh": "你好"
        },
        "natural language processing is amazing!": {
            "te": "సహజ భాషా ప్రాసెసింగ్ అద్భుతమైనది!",
            "hi": "प्राकृतिक भाषा प्रसंस्करण अद्भुत है!",
            "fr": "Le traitement du langage naturel est formidable !",
            "es": "¡El procesamiento del lenguaje natural es increíble!",
            "de": "Die Verarbeitung natürlicher Sprache ist erstaunlich!",
            "ja": "自然言語処理は素晴らしいです！",
            "zh": "自然语言处理太棒了！"
        }
    }

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        clean = text.strip().lower()
        if clean in self.DICTIONARY and target_lang in self.DICTIONARY[clean]:
            return self.DICTIONARY[clean][target_lang]
        # Meaningful mock placeholder indicating translation target
        return f"[{SUPPORTED_LANGUAGES.get(target_lang, target_lang)} translation of: {text}]"

    def get_supported_languages(self) -> Dict[str, str]:
        return SUPPORTED_LANGUAGES

class MyMemoryTranslationProvider(BaseTranslationProvider):
    """
    Public translation provider using MyMemory Translation API.
    Free tier allows up to 5000 chars/day without registration.
    """
    API_URL = "https://api.mymemory.translated.net/get"

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        try:
            params = {
                "q": text[:1000],  # Respect safe chunk limits
                "langpair": f"{source_lang}|{target_lang}"
            }
            res = requests.get(self.API_URL, params=params, timeout=5)
            if res.status_code == 200:
                data = res.json()
                if "responseData" in data and "translatedText" in data["responseData"]:
                    return data["responseData"]["translatedText"]
        except Exception:
            pass
        
        # Fallback to mock deterministic translation if external network request fails or rate limits
        return MockTranslationProvider().translate(text, source_lang, target_lang)

    def get_supported_languages(self) -> Dict[str, str]:
        return SUPPORTED_LANGUAGES

def get_translation_provider(provider_type: str = "mock") -> BaseTranslationProvider:
    if provider_type == "mymemory":
        return MyMemoryTranslationProvider()
    return MockTranslationProvider()
