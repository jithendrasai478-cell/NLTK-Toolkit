import os
from typing import Any, Dict
from backend.providers.translation_provider import (
    SUPPORTED_LANGUAGES, 
    get_translation_provider
)
from backend.utils.error_handlers import APIException

def get_languages() -> Dict[str, Any]:
    """Return all supported translation language codes and display names."""
    return {
        "supported_languages": [
            {"code": code, "name": name} for code, name in SUPPORTED_LANGUAGES.items()
        ],
        "total_languages": len(SUPPORTED_LANGUAGES)
    }

def translate_text(text: str, source_lang: str = "en", target_lang: str = "te") -> Dict[str, Any]:
    """Translate text between supported languages."""
    if source_lang not in SUPPORTED_LANGUAGES:
        raise APIException("UNSUPPORTED_LANGUAGE", f"Source language '{source_lang}' is not supported.", status_code=400)

    if target_lang not in SUPPORTED_LANGUAGES:
        raise APIException("UNSUPPORTED_LANGUAGE", f"Target language '{target_lang}' is not supported.", status_code=400)

    if source_lang == target_lang:
        return {
            "original_text": text,
            "translated_text": text,
            "source_language": source_lang,
            "target_language": target_lang,
            "provider": "identity",
            "notice": "Source and target languages are identical."
        }

    # Try Hugging Face NLLB-200 Neural Machine Translation if available
    try:
        from backend.providers.huggingface_provider import hf_translate_text
        hf_res = hf_translate_text(text, source_lang=source_lang, target_lang=target_lang)
        if hf_res:
            hf_res["source_language_name"] = SUPPORTED_LANGUAGES[source_lang]
            hf_res["target_language_name"] = SUPPORTED_LANGUAGES[target_lang]
            hf_res["character_count"] = len(text)
            return hf_res
    except Exception:
        pass

    provider_type = os.getenv("TRANSLATION_PROVIDER", "mymemory")
    provider = get_translation_provider(provider_type)
    translated = provider.translate(text, source_lang, target_lang)

    return {
        "original_text": text,
        "translated_text": translated,
        "source_language": source_lang,
        "source_language_name": SUPPORTED_LANGUAGES[source_lang],
        "target_language": target_lang,
        "target_language_name": SUPPORTED_LANGUAGES[target_lang],
        "character_count": len(text),
        "provider": provider_type
    }
