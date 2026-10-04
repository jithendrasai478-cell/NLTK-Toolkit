import os
import re
from pathlib import Path
from typing import Any, Dict
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords as nltk_stopwords

BASE_DIR = Path(__file__).resolve().parent.parent
LANG_MODEL_PATH = BASE_DIR / "data" / "models" / "language_detector.joblib"

_lang_pipeline = None

def get_language_model():
    global _lang_pipeline
    if _lang_pipeline is None and LANG_MODEL_PATH.exists():
        try:
            _lang_pipeline = joblib.load(LANG_MODEL_PATH)
        except Exception:
            _lang_pipeline = None
    return _lang_pipeline

LANG_NAMES = {
    "te": "Telugu (తెలుగు)",
    "hi": "Hindi (हिन्दी)",
    "ta": "Tamil (தமிழ்)",
    "kn": "Kannada (ಕನ್ನಡ)",
    "ml": "Malayalam (മലയാളം)",
    "bn": "Bengali (বাংলা)",
    "ur": "Urdu (اردو)",
    "en": "English",
    "fr": "French (Français)",
    "es": "Spanish (Español)",
    "de": "German (Deutsch)",
    "ja": "Japanese (日本語)",
    "zh": "Chinese (中文)"
}

SCRIPT_PATTERNS = [
    (re.compile(r'[\u0C00-\u0C7F]'), "te", "Telugu (తెలుగు)"),
    (re.compile(r'[\u0900-\u097F]'), "hi", "Hindi (हिन्दी)"),
    (re.compile(r'[\u0B80-\u0BFF]'), "ta", "Tamil (தமிழ்)"),
    (re.compile(r'[\u0C80-\u0CFF]'), "kn", "Kannada (ಕನ್ನಡ)"),
    (re.compile(r'[\u0D00-\u0D7F]'), "ml", "Malayalam (മലയാളം)"),
    (re.compile(r'[\u0980-\u09FF]'), "bn", "Bengali (বাংলা)"),
    (re.compile(r'[\u0600-\u06FF]'), "ur", "Urdu (اردو)"),
    (re.compile(r'[\u3040-\u30FF\u31F0-\u31FF]'), "ja", "Japanese (日本語)"),
    (re.compile(r'[\u4E00-\u9FFF]'), "zh", "Chinese (中文)"),
]

def detect_language(text: str) -> Dict[str, Any]:
    """
    Detect the language of the input text using:
    1. Unicode script pattern matching (highest confidence for Indian & CJK scripts)
    2. Trained Character N-gram Statistical ML Model (WiLI & Multilingual benchmark)
    3. Lexical stopword profile analysis (fallback for Latin scripts)
    """
    total_chars = max(1, len(text))

    # 1. Non-Latin Unicode Script Range Identification
    for pattern, code, name in SCRIPT_PATTERNS:
        matches = pattern.findall(text)
        if len(matches) >= 3 or (len(matches) > 0 and len(matches) / total_chars > 0.2):
            confidence = round(min(1.0, max(0.88, len(matches) / total_chars * 1.5)), 2)
            return {
                "language_code": code,
                "language_name": name,
                "confidence": confidence,
                "method": "Unicode Script Range Identification",
                "is_reliable": True,
                "character_matches": len(matches)
            }

    # 2. Machine Learning Character N-gram Classifier
    pipeline = get_language_model()
    if pipeline and len(text.strip()) >= 5:
        try:
            pred_code = str(pipeline.predict([text])[0])
            probs = pipeline.predict_proba([text])[0]
            max_prob = float(max(probs))
            if max_prob >= 0.35:
                return {
                    "language_code": pred_code,
                    "language_name": LANG_NAMES.get(pred_code, pred_code),
                    "confidence": round(max_prob, 4),
                    "method": "Character N-gram Statistical Classifier (Multilingual Benchmark)",
                    "is_reliable": max_prob >= 0.50
                }
        except Exception:
            pass

    # 3. Latin stopword profiling fallback
    words = set(re.findall(r'\b[a-zA-Z]{2,}\b', text.lower()))
    candidate_languages = ["english", "french", "spanish", "german", "italian"]
    best_lang = "english"
    max_overlap = 0

    for lang in candidate_languages:
        try:
            stops = set(nltk_stopwords.words(lang))
            overlap = len(words.intersection(stops))
            if overlap > max_overlap:
                max_overlap = overlap
                best_lang = lang
        except Exception:
            pass

    lang_codes = {"english": "en", "french": "fr", "spanish": "es", "german": "de", "italian": "it"}
    code = lang_codes.get(best_lang, "en")
    confidence = 0.90 if max_overlap >= 3 else 0.70 if max_overlap >= 1 else 0.50

    return {
        "language_code": code,
        "language_name": LANG_NAMES.get(code, "English"),
        "confidence": confidence,
        "method": "Lexical Stopword Profile Analysis",
        "is_reliable": max_overlap >= 2
    }

def calculate_similarity(text1: str, text2: str) -> Dict[str, Any]:
    """
    Calculate semantic and lexical similarity between two texts.
    Uses multi-level TF-IDF (word n-grams and character n-grams)
    with complete Unicode script preservation (Telugu, Indic, Latin).
    """
    clean1 = text1.strip()
    clean2 = text2.strip()

    if not clean1 or not clean2:
        return {
            "similarity_score": 0.0,
            "similarity_percentage": 0.0,
            "verdict": "Empty input text.",
            "shared_keywords": []
        }

    # 1. Word-level similarity with Unicode token pattern
    word_sim = 0.0
    try:
        word_vectorizer = TfidfVectorizer(
            token_pattern=r'(?u)\b[\w\'-]+\b',
            ngram_range=(1, 2)
        )
        word_tfidf = word_vectorizer.fit_transform([clean1, clean2])
        word_sim = float(cosine_similarity(word_tfidf[0:1], word_tfidf[1:2])[0][0])
    except Exception:
        word_sim = 0.0

    # 2. Character 3-gram similarity (detects morphological roots and subword overlap)
    char_sim = 0.0
    try:
        char_vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 4)
        )
        char_tfidf = char_vectorizer.fit_transform([clean1, clean2])
        char_sim = float(cosine_similarity(char_tfidf[0:1], char_tfidf[1:2])[0][0])
    except Exception:
        char_sim = word_sim

    # Weighted blended similarity score
    sim_score = (word_sim * 0.65) + (char_sim * 0.35)
    score = round(max(0.0, min(1.0, sim_score)), 4)
    percentage = round(score * 100, 1)

    if score >= 0.80:
        verdict = "Very High Similarity (Substantially Identical Phrasing)"
    elif score >= 0.55:
        verdict = "High Similarity (Strong Thematic & Concept Overlap)"
    elif score >= 0.30:
        verdict = "Moderate Similarity (Partial Shared Vocabulary)"
    elif score >= 0.12:
        verdict = "Low Similarity (Minor Lexical Association)"
    else:
        verdict = "Very Low / No Similarity (Distinct Topics)"

    # Identify shared terms (Unicode aware)
    words1 = set(re.findall(r'(?u)\b[\w\'-]{2,}\b', clean1.lower()))
    words2 = set(re.findall(r'(?u)\b[\w\'-]{2,}\b', clean2.lower()))
    shared = sorted(words1.intersection(words2))[:10]

    return {
        "similarity_score": score,
        "similarity_percentage": percentage,
        "verdict": verdict,
        "components": {
            "word_similarity": round(word_sim, 4),
            "character_subword_similarity": round(char_sim, 4)
        },
        "shared_terms": shared,
        "shared_keywords": shared,
        "method": "Blended Word & Character-Ngram Cosine Vectorization (STS Benchmark Aligned)"
    }
