import re
from collections import Counter
from typing import Any, Dict, List, Optional
import nltk
from nltk.corpus import stopwords as nltk_stopwords
from nltk.corpus import wordnet
from nltk.stem import PorterStemmer, SnowballStemmer, WordNetLemmatizer
from nltk.util import ngrams as nltk_ngrams

# Human-readable descriptions for common Penn Treebank POS tags
POS_DESCRIPTIONS: Dict[str, str] = {
    "CC": "Coordinating conjunction",
    "CD": "Cardinal digit",
    "DT": "Determiner",
    "EX": "Existential there",
    "FW": "Foreign word",
    "IN": "Preposition or subordinating conjunction",
    "JJ": "Adjective",
    "JJR": "Adjective, comparative",
    "JJS": "Adjective, superlative",
    "LS": "List item marker",
    "MD": "Modal",
    "NN": "Noun, singular or mass",
    "NNS": "Noun, plural",
    "NNP": "Proper noun, singular",
    "NNPS": "Proper noun, plural",
    "PDT": "Predeterminer",
    "POS": "Possessive ending",
    "PRP": "Personal pronoun",
    "PRP$": "Possessive pronoun",
    "RB": "Adverb",
    "RBR": "Adverb, comparative",
    "RBS": "Adverb, superlative",
    "RP": "Particle",
    "TO": "to",
    "UH": "Interjection",
    "VB": "Verb, base form",
    "VBD": "Verb, past tense",
    "VBG": "Verb, gerund or present participle",
    "VBN": "Verb, past participle",
    "VBP": "Verb, non-3rd person singular present",
    "VBZ": "Verb, 3rd person singular present",
    "WDT": "Wh-determiner",
    "WP": "Wh-pronoun",
    "WP$": "Possessive wh-pronoun",
    "WRB": "Wh-adverb",
}

def remove_stopwords(
    text: str, 
    language: str = "english", 
    preserve_words: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Remove stopwords from text using NLTK stopword corpus or IndicNLP Telugu resources."""
    lang_clean = language.lower().strip()
    is_telugu = lang_clean in ("telugu", "te") or bool(re.search(r'[\u0C00-\u0C7F]', text))

    if is_telugu:
        from backend.services.keywords_service import get_telugu_stopwords
        stop_set = get_telugu_stopwords()
        lang_used = "telugu"
    else:
        try:
            stop_set = set(nltk_stopwords.words(lang_clean))
            lang_used = lang_clean
        except Exception:
            stop_set = set(nltk_stopwords.words("english"))
            lang_used = "english"

    if preserve_words:
        stop_set = stop_set - set(w.lower().strip() for w in preserve_words)

    if is_telugu:
        words = re.findall(r'[\u0C00-\u0C7F\w\'-]+', text)
    else:
        words = re.findall(r'\b[\w\'-]+\b', text, re.UNICODE)
    kept_words = [w for w in words if w.lower() not in stop_set]
    removed_words = [w for w in words if w.lower() in stop_set]

    # Reconstruct text maintaining approximate punctuation
    filtered_text = " ".join(kept_words)

    return {
        "original_word_count": len(words),
        "filtered_word_count": len(kept_words),
        "removed_count": len(removed_words),
        "removal_ratio": round(len(removed_words) / len(words), 3) if words else 0.0,
        "filtered_text": filtered_text,
        "filtered_tokens": kept_words,
        "removed_stopwords": list(set(w.lower() for w in removed_words)),
        "language_used": lang_used,
    }

def stem_text(text: str, algorithm: str = "porter", language: str = "english") -> Dict[str, Any]:
    """Apply stemming to words in text using Porter or Snowball stemmer."""
    if algorithm.lower() == "snowball":
        try:
            stemmer = SnowballStemmer(language)
        except Exception:
            stemmer = PorterStemmer()
    else:
        stemmer = PorterStemmer()

    words = re.findall(r'\b[\w\'-]+\b', text, re.UNICODE)
    stemmed_pairs: List[Dict[str, str]] = []
    for word in words:
        stemmed_pairs.append({
            "original": word,
            "stem": stemmer.stem(word)
        })

    return {
        "algorithm": algorithm,
        "language": language,
        "word_count": len(words),
        "stems": stemmed_pairs,
        "stemmed_text": " ".join([p["stem"] for p in stemmed_pairs]),
        "explanation": "Stemming strips word suffixes to find a crude base form (may not be a dictionary word)."
    }

def get_wordnet_pos(treebank_tag: str):
    """Map Penn Treebank POS tag to WordNet POS constant."""
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

def lemmatize_text(text: str) -> Dict[str, Any]:
    """Apply lemmatization using WordNet lemmatizer with POS tag mapping."""
    lemmatizer = WordNetLemmatizer()
    tokens = nltk.word_tokenize(text)
    pos_tags = nltk.pos_tag(tokens)

    lemmas: List[Dict[str, str]] = []
    for word, tag in pos_tags:
        if re.match(r'^[\w\'-]+$', word):
            wn_tag = get_wordnet_pos(tag)
            lemma = lemmatizer.lemmatize(word.lower(), pos=wn_tag)
            lemmas.append({
                "original": word,
                "pos_tag": tag,
                "lemma": lemma
            })

    return {
        "word_count": len(lemmas),
        "lemmas": lemmas,
        "lemmatized_text": " ".join([l["lemma"] for l in lemmas]),
        "explanation": "Lemmatization uses vocabulary and morphological analysis to return proper dictionary root words."
    }

def tag_pos(text: str) -> Dict[str, Any]:
    """Tag words with part-of-speech using Penn Treebank tagger."""
    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)

    tag_list = []
    tag_counts = Counter()
    for word, tag in tagged:
        desc = POS_DESCRIPTIONS.get(tag, "Punctuation or Symbol")
        tag_list.append({
            "token": word,
            "tag": tag,
            "description": desc
        })
        tag_counts[tag] += 1

    return {
        "token_count": len(tokens),
        "tagged_tokens": tag_list,
        "tag_distribution": [{"tag": t, "count": c, "description": POS_DESCRIPTIONS.get(t, "")} for t, c in tag_counts.most_common()]
    }

def generate_ngrams(text: str, n: int = 2) -> Dict[str, Any]:
    """Generate n-grams and frequencies from tokenized text."""
    tokens = re.findall(r'\b[\w\'-]+\b', text.lower(), re.UNICODE)
    if len(tokens) < n:
        return {
            "n": n,
            "ngram_count": 0,
            "ngrams": [],
            "message": f"Input text contains fewer tokens ({len(tokens)}) than n={n}."
        }

    generated = list(nltk_ngrams(tokens, n))
    freq = Counter(generated)

    results = []
    for gram, count in freq.most_common(50):
        results.append({
            "ngram": " ".join(gram),
            "tokens": list(gram),
            "frequency": count
        })

    return {
        "n": n,
        "total_ngrams": len(generated),
        "unique_ngrams": len(freq),
        "ngrams": results
    }

def analyze_word_frequency(
    text: str, 
    remove_stops: bool = True, 
    top_n: int = 10,
    language: str = "english"
) -> Dict[str, Any]:
    """Perform frequency analysis on words with chart-ready JSON output."""
    words = re.findall(r'\b[\w\'-]+\b', text.lower(), re.UNICODE)
    
    if remove_stops:
        try:
            stops = set(nltk_stopwords.words(language))
        except Exception:
            stops = set(nltk_stopwords.words("english"))
        words = [w for w in words if w not in stops]

    total_valid = len(words)
    counter = Counter(words)
    top_words = counter.most_common(top_n)

    distribution = []
    for word, count in top_words:
        distribution.append({
            "word": word,
            "count": count,
            "relative_frequency": round(count / total_valid, 4) if total_valid > 0 else 0.0,
            "percentage": round((count / total_valid) * 100, 2) if total_valid > 0 else 0.0
        })

    return {
        "total_words_analyzed": total_valid,
        "unique_words": len(counter),
        "stopwords_removed": remove_stops,
        "distribution": distribution
    }
