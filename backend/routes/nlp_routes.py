import time
from flask import Blueprint, request
from backend.utils.error_handlers import api_success, APIException
from backend.utils.validators import (
    validate_json_body, 
    validate_text_input, 
    validate_choice, 
    validate_int_range
)
from backend.services.summarizer_service import summarize_text
from backend.services.sentiment_service import analyze_sentiment
from backend.services.keywords_service import extract_keywords
from backend.services.tokenizer_service import tokenize_text
from backend.services.classifier_service import classify_text, train_custom_classifier, get_classifier_diagnostics
from backend.services.translator_service import translate_text, get_languages
from backend.services.rewriter_service import rewrite_text
from backend.services.qa_service import answer_question
from backend.services.ner_service import extract_entities
from backend.services.statistics_service import calculate_statistics, calculate_readability
from backend.services.linguistics_service import (
    remove_stopwords,
    stem_text,
    lemmatize_text,
    tag_pos,
    generate_ngrams,
    analyze_word_frequency
)
from backend.services.language_service import detect_language, calculate_similarity

nlp_bp = Blueprint("nlp", __name__, url_prefix="/api/v1")

def timed_execution(func, *args, **kwargs):
    """Execute function and return result with elapsed execution time in ms."""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    return result, elapsed_ms

import json
from pathlib import Path

# ==================== Datasets & Models Transparency ====================
@nlp_bp.route("/datasets", methods=["GET"])
def list_datasets():
    manifest_path = Path(__file__).resolve().parent.parent / "data" / "manifests" / "datasets.json"
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"total_datasets": 0, "datasets": []}
    return api_success(data, meta={"tool": "datasets"})

@nlp_bp.route("/models/status", methods=["GET"])
def get_models_status():
    report_path = Path(__file__).resolve().parent.parent / "reports" / "model_evaluation" / "model_evaluation_report.json"
    if report_path.exists():
        with open(report_path, "r", encoding="utf-8") as f:
            eval_data = json.load(f)
    else:
        eval_data = {}
    return api_success(eval_data, meta={"tool": "models_status"})

# ==================== Language Listing ====================
@nlp_bp.route("/languages", methods=["GET"])
def list_languages():
    result, ms = timed_execution(get_languages)
    return api_success(result, meta={"tool": "languages", "processing_time_ms": ms})

# ==================== Core NLP Endpoints ====================

@nlp_bp.route("/nlp/summarize", methods=["POST"])
def endpoint_summarize():
    data = validate_json_body()
    text = validate_text_input(data)
    options = data.get("options", {})
    mode = options.get("summary_length", "medium")
    validate_choice(mode, ["short", "medium", "long"], "summary_length")

    result, ms = timed_execution(summarize_text, text, length_mode=mode)
    return api_success(result, meta={"tool": "summarize", "processing_time_ms": ms})

@nlp_bp.route("/nlp/sentiment", methods=["POST"])
def endpoint_sentiment():
    data = validate_json_body()
    text = validate_text_input(data)

    result, ms = timed_execution(analyze_sentiment, text)
    return api_success(result, meta={"tool": "sentiment", "processing_time_ms": ms})

@nlp_bp.route("/nlp/keywords", methods=["POST"])
def endpoint_keywords():
    data = validate_json_body()
    text = validate_text_input(data)
    options = data.get("options", {})
    top_n = validate_int_range(options.get("top_n", 10), 1, 50, "top_n")
    method = options.get("method", "tfidf")
    validate_choice(method, ["tfidf", "frequency"], "method")
    
    corpus_mode = options.get("corpus_mode", "single")
    validate_choice(corpus_mode, ["single", "multi_doc"], "corpus_mode")
    reference_corpus = options.get("reference_corpus")

    result, ms = timed_execution(
        extract_keywords, 
        text, 
        top_n=top_n, 
        method=method, 
        corpus_mode=corpus_mode, 
        reference_corpus=reference_corpus
    )
    return api_success(result, meta={"tool": "keywords", "processing_time_ms": ms})

@nlp_bp.route("/nlp/tokenize", methods=["POST"])
def endpoint_tokenize():
    data = validate_json_body()
    text = validate_text_input(data)
    options = data.get("options", {})
    lang = options.get("language", "english")

    result, ms = timed_execution(tokenize_text, text, language=lang)
    return api_success(result, meta={"tool": "tokenize", "processing_time_ms": ms})

@nlp_bp.route("/nlp/classify", methods=["POST"])
def endpoint_classify():
    data = validate_json_body()
    text = validate_text_input(data)

    result, ms = timed_execution(classify_text, text)
    return api_success(result, meta={"tool": "classify", "processing_time_ms": ms})

@nlp_bp.route("/nlp/classify/diagnostics", methods=["GET"])
def endpoint_classify_diagnostics():
    result, ms = timed_execution(get_classifier_diagnostics)
    return api_success(result, meta={"tool": "classify-diagnostics", "processing_time_ms": ms})

@nlp_bp.route("/nlp/custom-classify", methods=["POST"])
def endpoint_custom_classify():
    data = validate_json_body()
    test_text = validate_text_input(data, "test_text")
    examples = data.get("training_examples")
    if not isinstance(examples, list) or not examples:
        raise APIException("MISSING_EXAMPLES", "Field 'training_examples' must be a non-empty list.", status_code=400)

    result, ms = timed_execution(train_custom_classifier, examples, test_text)
    return api_success(result, meta={"tool": "custom-classify", "processing_time_ms": ms})

@nlp_bp.route("/nlp/translate", methods=["POST"])
def endpoint_translate():
    data = validate_json_body()
    text = validate_text_input(data)
    source_lang = data.get("source_language", "en")
    target_lang = data.get("target_language", "te")

    result, ms = timed_execution(translate_text, text, source_lang=source_lang, target_lang=target_lang)
    return api_success(result, meta={"tool": "translate", "processing_time_ms": ms})

@nlp_bp.route("/nlp/rewrite", methods=["POST"])
def endpoint_rewrite():
    data = validate_json_body()
    text = validate_text_input(data)
    options = data.get("options", {})
    mode = options.get("mode", "simplify")

    result, ms = timed_execution(rewrite_text, text, mode=mode)
    return api_success(result, meta={"tool": "rewrite", "processing_time_ms": ms})

@nlp_bp.route("/nlp/qa", methods=["POST"])
def endpoint_qa():
    data = validate_json_body()
    passage = validate_text_input(data, "passage")
    question = validate_text_input(data, "question")

    result, ms = timed_execution(answer_question, passage=passage, question=question)
    return api_success(result, meta={"tool": "qa", "processing_time_ms": ms})

@nlp_bp.route("/nlp/ner", methods=["POST"])
def endpoint_ner():
    data = validate_json_body()
    text = validate_text_input(data)

    result, ms = timed_execution(extract_entities, text)
    return api_success(result, meta={"tool": "ner", "processing_time_ms": ms})

@nlp_bp.route("/nlp/statistics", methods=["POST"])
def endpoint_statistics():
    data = validate_json_body()
    text = validate_text_input(data)

    result, ms = timed_execution(calculate_statistics, text)
    return api_success(result, meta={"tool": "statistics", "processing_time_ms": ms})

@nlp_bp.route("/nlp/readability", methods=["POST"])
def endpoint_readability():
    data = validate_json_body()
    text = validate_text_input(data)

    result, ms = timed_execution(calculate_readability, text)
    return api_success(result, meta={"tool": "readability", "processing_time_ms": ms})

@nlp_bp.route("/nlp/stopwords", methods=["POST"])
def endpoint_stopwords():
    data = validate_json_body()
    text = validate_text_input(data)
    options = data.get("options", {})
    lang = options.get("language", "english")
    preserve = options.get("preserve_words", [])

    result, ms = timed_execution(remove_stopwords, text, language=lang, preserve_words=preserve)
    return api_success(result, meta={"tool": "stopwords", "processing_time_ms": ms})

@nlp_bp.route("/nlp/stem", methods=["POST"])
def endpoint_stem():
    data = validate_json_body()
    text = validate_text_input(data)
    options = data.get("options", {})
    algo = options.get("algorithm", "porter")
    lang = options.get("language", "english")

    result, ms = timed_execution(stem_text, text, algorithm=algo, language=lang)
    return api_success(result, meta={"tool": "stem", "processing_time_ms": ms})

@nlp_bp.route("/nlp/lemmatize", methods=["POST"])
def endpoint_lemmatize():
    data = validate_json_body()
    text = validate_text_input(data)

    result, ms = timed_execution(lemmatize_text, text)
    return api_success(result, meta={"tool": "lemmatize", "processing_time_ms": ms})

@nlp_bp.route("/nlp/pos-tag", methods=["POST"])
def endpoint_pos_tag():
    data = validate_json_body()
    text = validate_text_input(data)

    result, ms = timed_execution(tag_pos, text)
    return api_success(result, meta={"tool": "pos-tag", "processing_time_ms": ms})

@nlp_bp.route("/nlp/ngrams", methods=["POST"])
def endpoint_ngrams():
    data = validate_json_body()
    text = validate_text_input(data)
    options = data.get("options", {})
    n = validate_int_range(options.get("n", 2), 1, 5, "n")

    result, ms = timed_execution(generate_ngrams, text, n=n)
    return api_success(result, meta={"tool": "ngrams", "processing_time_ms": ms})

@nlp_bp.route("/nlp/word-frequency", methods=["POST"])
def endpoint_word_frequency():
    data = validate_json_body()
    text = validate_text_input(data)
    options = data.get("options", {})
    remove_stops = bool(options.get("remove_stopwords", True))
    top_n = validate_int_range(options.get("top_n", 10), 1, 100, "top_n")

    result, ms = timed_execution(analyze_word_frequency, text, remove_stops=remove_stops, top_n=top_n)
    return api_success(result, meta={"tool": "word-frequency", "processing_time_ms": ms})

@nlp_bp.route("/nlp/language-detection", methods=["POST"])
def endpoint_language_detection():
    data = validate_json_body()
    text = validate_text_input(data)

    result, ms = timed_execution(detect_language, text)
    return api_success(result, meta={"tool": "language-detection", "processing_time_ms": ms})

@nlp_bp.route("/nlp/similarity", methods=["POST"])
def endpoint_similarity():
    data = validate_json_body()
    text1 = validate_text_input(data, "text1")
    text2 = validate_text_input(data, "text2")

    result, ms = timed_execution(calculate_similarity, text1, text2)
    return api_success(result, meta={"tool": "similarity", "processing_time_ms": ms})
