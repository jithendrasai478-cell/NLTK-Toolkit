import re
from collections import Counter
from typing import Any, Dict, List
import nltk

def count_syllables(word: str) -> int:
    """Heuristic syllable counter for English words."""
    word = word.lower().strip()
    if len(word) <= 3:
        return 1
    # Remove silent trailing e
    word = re.sub(r'(?:[^laeiouy]|ed|es|e)$', '', word)
    word = re.sub(r'^y', '', word)
    vowels = re.findall(r'[aeiouy]{1,2}', word)
    return max(1, len(vowels))

def calculate_statistics(text: str) -> Dict[str, Any]:
    """Calculate comprehensive text statistics."""
    # Sentence splitting
    try:
        sentences = nltk.sent_tokenize(text)
    except Exception:
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    sentence_count = max(1, len(sentences))

    # Words splitting (alphanumeric words only for accurate word counts)
    words = re.findall(r'\b[\w\'-]+\b', text, re.UNICODE)
    word_count = len(words)

    # Paragraphs
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    paragraph_count = max(1, len(paragraphs))

    char_count = len(text)
    char_count_no_spaces = len(re.sub(r'\s+', '', text))

    avg_word_len = round(sum(len(w) for w in words) / word_count, 2) if word_count > 0 else 0.0
    avg_sentence_len = round(word_count / sentence_count, 2) if sentence_count > 0 else 0.0

    longest_word = max(words, key=len) if words else ""

    # Frequency of cleaned lowercase words
    lower_words = [w.lower() for w in words]
    word_freq = Counter(lower_words).most_common(5)

    # Reading time estimate: average reading speed is ~225 words per minute
    reading_time_minutes = round(word_count / 225, 2) if word_count > 0 else 0.0
    reading_time_seconds = max(1, round(word_count / 225 * 60)) if word_count > 0 else 0

    return {
        "character_count": char_count,
        "character_count_no_spaces": char_count_no_spaces,
        "word_count": word_count,
        "sentence_count": len(sentences),
        "paragraph_count": paragraph_count,
        "average_word_length": avg_word_len,
        "average_sentence_length": avg_sentence_len,
        "longest_word": longest_word,
        "longest_word_length": len(longest_word),
        "top_frequent_words": [{"word": w, "count": c} for w, c in word_freq],
        "estimated_reading_time": {
            "minutes": reading_time_minutes,
            "seconds": reading_time_seconds,
            "formatted": f"{reading_time_seconds} sec" if reading_time_seconds < 60 else f"{reading_time_minutes} min"
        }
    }

def calculate_readability(text: str) -> Dict[str, Any]:
    """Calculate Flesch Reading Ease and Flesch-Kincaid Grade Level."""
    stats = calculate_statistics(text)
    word_count = stats["word_count"]
    sentence_count = stats["sentence_count"]

    if word_count < 5 or sentence_count < 1:
        return {
            "flesch_reading_ease": 0.0,
            "flesch_kincaid_grade": 0.0,
            "reading_level": "Insufficient Text",
            "warning": "At least 5 words and 1 complete sentence are required for reliable readability estimation.",
            "metrics": stats
        }

    words = re.findall(r'\b[\w\'-]+\b', text)
    total_syllables = sum(count_syllables(w) for w in words)

    # Standard Flesch Reading Ease formula
    fre = 206.835 - (1.015 * (word_count / sentence_count)) - (84.6 * (total_syllables / word_count))
    fre = round(max(0.0, min(100.0, fre)), 2)

    # Flesch-Kincaid Grade Level formula
    fkgl = (0.39 * (word_count / sentence_count)) + (11.8 * (total_syllables / word_count)) - 15.59
    fkgl = round(max(0.0, fkgl), 1)

    if fre >= 90:
        level = "Very Easy (5th grade reading level)"
    elif fre >= 80:
        level = "Easy (6th grade reading level)"
    elif fre >= 70:
        level = "Fairly Easy (7th grade reading level)"
    elif fre >= 60:
        level = "Standard (8th - 9th grade reading level)"
    elif fre >= 50:
        level = "Fairly Difficult (10th - 12th grade level)"
    elif fre >= 30:
        level = "Difficult (College level)"
    else:
        level = "Very Difficult (Graduate / Professional level)"

    is_indic = bool(re.search(r'[\u0900-\u0D7F]', text))
    if is_indic:
        note = (
            "NOTICE: Non-Latin Indic/Telugu script detected. Flesch Reading Ease and Flesch-Kincaid "
            "formulas are calibrated exclusively for English prose. For Indic languages, character "
            "and word statistics serve as morphological complexity indicators."
        )
    else:
        note = "Standard Flesch Reading Ease and Flesch-Kincaid Grade Level formulas calibrated for English prose."

    return {
        "flesch_reading_ease": fre,
        "flesch_kincaid_grade": fkgl,
        "reading_level": level,
        "total_syllables": total_syllables,
        "average_syllables_per_word": round(total_syllables / word_count, 2),
        "metrics": {
            "word_count": word_count,
            "sentence_count": sentence_count,
        },
        "note": note
    }
