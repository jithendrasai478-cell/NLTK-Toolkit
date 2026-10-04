import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
load_dotenv()

# Hugging Face Router API endpoints
HF_ROUTER_BASE = "https://router.huggingface.co/hf-inference/models"

# Default state-of-the-art transformer models (aligned with ChatGPT NLP recommendations)
DEFAULT_SUMMARIZATION_MODEL = "facebook/bart-large-cnn"
DEFAULT_TRANSLATION_MODEL = "facebook/nllb-200-distilled-600M"
DEFAULT_QA_MODEL = "deepset/roberta-base-squad2"
DEFAULT_SENTIMENT_MODEL = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
DEFAULT_CLASSIFICATION_MODEL = "facebook/bart-large-mnli"
DEFAULT_NER_MODEL = "dslim/bert-base-NER"
DEFAULT_REWRITE_MODEL = "Vamsi/T5_Paraphrase_Paws"

# NLLB-200 BCP-47 language tag mappings for multi-lingual translation
NLLB_LANGUAGE_MAP = {
    "te": "tel_Telu",  # Telugu
    "hi": "hin_Deva",  # Hindi
    "ta": "tam_Taml",  # Tamil
    "kn": "kan_Knda",  # Kannada
    "ml": "mal_Mlym",  # Malayalam
    "bn": "ben_Beng",  # Bengali
    "mr": "mar_Deva",  # Marathi
    "ur": "urd_Arab",  # Urdu
    "en": "eng_Latn",  # English
    "fr": "fra_Latn",  # French
    "es": "spa_Latn",  # Spanish
    "de": "deu_Latn",  # German
    "ja": "jpn_Jpan",  # Japanese
    "zh": "zho_Hans",  # Chinese (Simplified)
}

def get_hf_token() -> Optional[str]:
    """Retrieve Hugging Face API key from environment."""
    return os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN")

def get_hf_headers() -> Dict[str, str]:
    token = get_hf_token()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token.strip()}"
    return headers

def call_hf_api(model_name: str, payload: Dict[str, Any], timeout: int = 25) -> Tuple[Optional[Any], Optional[str]]:
    """
    Executes a POST request to the Hugging Face Router Inference endpoint.
    Returns (response_data, error_message).
    """
    token = get_hf_token()
    if not token:
        return None, "No Hugging Face API token configured."

    url = f"{HF_ROUTER_BASE}/{model_name}"
    headers = get_hf_headers()

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=timeout)
        if res.status_code == 200:
            return res.json(), None
        elif res.status_code == 503:
            # Model is currently loading on HF servers
            data = res.json() if res.content else {}
            eta = data.get("estimated_time", 20)
            return None, f"Model '{model_name}' is currently initializing on Hugging Face (est. {eta}s)."
        elif res.status_code == 403:
            return None, "HF token lacks 'Make calls to the serverless Inference API' permission."
        elif res.status_code == 401:
            return None, "Invalid Hugging Face API token."
        else:
            err = res.text[:200]
            return None, f"Hugging Face API returned status {res.status_code}: {err}"
    except requests.exceptions.Timeout:
        return None, "Hugging Face request timed out."
    except Exception as e:
        return None, f"Network error communicating with Hugging Face: {str(e)}"


# =====================================================================
# 1. Summarization: facebook/bart-large-cnn & T5
# =====================================================================
def hf_summarize_text(text: str, length_mode: str = "medium") -> Optional[Dict[str, Any]]:
    """Summarize text using BART-large-CNN or T5 via Hugging Face."""
    token = get_hf_token()
    if not token:
        return None

    model_name = os.getenv("HUGGINGFACE_SUMMARIZATION_MODEL", DEFAULT_SUMMARIZATION_MODEL)

    word_count = len(text.split())
    if length_mode == "short":
        max_len = max(30, min(80, word_count // 2))
        min_len = 15
    elif length_mode == "long":
        max_len = max(90, min(200, int(word_count * 0.7)))
        min_len = 50
    else:  # medium
        max_len = max(60, min(140, int(word_count * 0.5)))
        min_len = 30

    payload = {
        "inputs": text,
        "parameters": {
            "max_length": max_len,
            "min_length": min_len,
            "do_sample": False
        }
    }

    data, err = call_hf_api(model_name, payload, timeout=30)
    if not data or err:
        return None

    summary_text = ""
    if isinstance(data, list) and len(data) > 0 and "summary_text" in data[0]:
        summary_text = data[0]["summary_text"].strip()
    elif isinstance(data, dict) and "summary_text" in data:
        summary_text = data["summary_text"].strip()

    if not summary_text:
        return None

    orig_words = len(text.split())
    sum_words = len(summary_text.split())
    compression = round(sum_words / max(1, orig_words), 3)

    return {
        "summary": summary_text,
        "original_word_count": orig_words,
        "summary_word_count": sum_words,
        "compression_ratio": compression,
        "percentage_reduction": round(max(0.0, (1 - compression) * 100), 1),
        "mode": length_mode,
        "provider": "huggingface_transformer",
        "model": model_name,
        "technique": "Neural Abstractive Summarization (BART/T5 Architecture)"
    }


# =====================================================================
# 2. Sentiment: distilbert-base-uncased-finetuned-sst-2-english
# =====================================================================
def hf_analyze_sentiment(text: str) -> Optional[Dict[str, Any]]:
    """Analyze sentiment using DistilBERT SST-2 via Hugging Face."""
    token = get_hf_token()
    if not token:
        return None

    model_name = os.getenv("HUGGINGFACE_SENTIMENT_MODEL", DEFAULT_SENTIMENT_MODEL)
    payload = {"inputs": text}

    data, err = call_hf_api(model_name, payload, timeout=20)
    if not data or err:
        return None

    # Format: [[{"label": "POSITIVE", "score": 0.99}, {"label": "NEGATIVE", "score": 0.01}]]
    items = data[0] if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list) else data
    if not isinstance(items, list):
        return None

    top_item = max(items, key=lambda x: x.get("score", 0.0))
    raw_label = top_item.get("label", "POSITIVE").upper()
    score = float(top_item.get("score", 0.0))

    label = "Positive" if "POS" in raw_label else "Negative" if "NEG" in raw_label else "Neutral"
    prob_dict = {it.get("label", "").title(): round(float(it.get("score", 0.0)), 4) for it in items}

    return {
        "predicted_label": label.lower(),
        "confidence": round(score, 4),
        "probabilities": prob_dict,
        "model": f"Hugging Face Transformer ({model_name})",
        "provider": "huggingface_transformer"
    }


# =====================================================================
# 3. Topic Classification: facebook/bart-large-mnli (Zero-Shot)
# =====================================================================
def hf_classify_text(text: str, candidate_labels: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
    """Zero-shot topic classification using BART-large-MNLI via Hugging Face."""
    token = get_hf_token()
    if not token:
        return None

    if candidate_labels is None:
        candidate_labels = [
            "Technology", "Business", "Sports", "Politics", "Science & Health", "Entertainment"
        ]

    model_name = os.getenv("HUGGINGFACE_CLASSIFICATION_MODEL", DEFAULT_CLASSIFICATION_MODEL)
    payload = {
        "inputs": text,
        "parameters": {
            "candidate_labels": candidate_labels
        }
    }

    data, err = call_hf_api(model_name, payload, timeout=25)
    if not data or err or not isinstance(data, dict):
        return None

    labels = data.get("labels", [])
    scores = data.get("scores", [])
    if not labels or not scores:
        return None

    scored_classes = []
    for lbl, scr in zip(labels, scores):
        scored_classes.append({
            "category": lbl,
            "confidence": round(float(scr), 4),
            "percentage": round(float(scr) * 100, 1)
        })

    top_conf = scored_classes[0]["confidence"]
    top_label = scored_classes[0]["category"]
    tier = "High" if top_conf >= 0.60 else "Moderate" if top_conf >= 0.35 else "Low"

    return {
        "predicted_category": top_label,
        "confidence": top_conf,
        "confidence_tier": tier,
        "category_probabilities": scored_classes,
        "model_info": {
            "algorithm": f"Zero-Shot NLI Transformer ({model_name})",
            "supported_categories": candidate_labels,
            "version": "Hugging Face Zero-Shot Pipeline"
        },
        "provider": "huggingface_transformer"
    }


# =====================================================================
# 4. Named Entity Recognition: dslim/bert-base-NER
# =====================================================================
def hf_extract_ner(text: str) -> Optional[Dict[str, Any]]:
    """Token classification / Named Entity Recognition using BERT-base-NER."""
    token = get_hf_token()
    if not token:
        return None

    model_name = os.getenv("HUGGINGFACE_NER_MODEL", DEFAULT_NER_MODEL)
    payload = {"inputs": text}

    data, err = call_hf_api(model_name, payload, timeout=25)
    if not data or err or not isinstance(data, list):
        return None

    label_map = {
        "PER": "Person",
        "B-PER": "Person",
        "I-PER": "Person",
        "LOC": "Location / Geo-Political Entity",
        "B-LOC": "Location / Geo-Political Entity",
        "I-LOC": "Location / Geo-Political Entity",
        "ORG": "Organization",
        "B-ORG": "Organization",
        "I-ORG": "Organization",
        "MISC": "Miscellaneous",
        "B-MISC": "Miscellaneous",
        "I-MISC": "Miscellaneous"
    }

    # Aggregate consecutive subwords and tokens
    entities = []
    from collections import Counter
    type_counts = Counter()

    for item in data:
        raw_entity = item.get("entity_group") or item.get("entity", "")
        word = item.get("word", "").replace("##", "").strip()
        score = float(item.get("score", 0.0))
        if not word or raw_entity == "O":
            continue

        cat = label_map.get(raw_entity, raw_entity)
        type_counts[cat] += 1
        entities.append({
            "text": word,
            "label": raw_entity,
            "category": cat,
            "score": round(score, 3),
            "start": item.get("start", 0),
            "end": item.get("end", 0),
            "sentence_index": 1
        })

    return {
        "total_entities_found": len(entities),
        "entities": entities,
        "category_breakdown": [{"category": cat, "count": cnt} for cat, cnt in type_counts.most_common()],
        "model": f"Hugging Face Transformer ({model_name} CoNLL-2003)",
        "provider": "huggingface_transformer"
    }


# =====================================================================
# 5. Translation: facebook/nllb-200-distilled-600M
# =====================================================================
def hf_translate_text(text: str, source_lang: str = "en", target_lang: str = "te") -> Optional[Dict[str, Any]]:
    """Translate text between 200 languages using Meta's NLLB-200."""
    token = get_hf_token()
    if not token:
        return None

    model_name = os.getenv("HUGGINGFACE_TRANSLATION_MODEL", DEFAULT_TRANSLATION_MODEL)
    src_tag = NLLB_LANGUAGE_MAP.get(source_lang, "eng_Latn")
    tgt_tag = NLLB_LANGUAGE_MAP.get(target_lang, "tel_Telu")

    payload = {
        "inputs": text,
        "parameters": {
            "src_lang": src_tag,
            "tgt_lang": tgt_tag
        }
    }

    data, err = call_hf_api(model_name, payload, timeout=30)
    if not data or err:
        return None

    translated_text = ""
    if isinstance(data, list) and len(data) > 0 and "translation_text" in data[0]:
        translated_text = data[0]["translation_text"].strip()
    elif isinstance(data, dict) and "translation_text" in data:
        translated_text = data["translation_text"].strip()

    if not translated_text:
        return None

    return {
        "original_text": text,
        "translated_text": translated_text,
        "source_language": source_lang,
        "target_language": target_lang,
        "provider": "huggingface_transformer",
        "model": model_name,
        "architecture": "NLLB-200 (No Language Left Behind Multilingual Transformer)"
    }


# =====================================================================
# 6. Rewriting / Paraphrase: Vamsi/T5_Paraphrase_Paws
# =====================================================================
def hf_rewrite_text(text: str, mode: str = "paraphrase") -> Optional[Dict[str, Any]]:
    """Generate fluent paraphrases using T5-Paraphrase-PAWS."""
    token = get_hf_token()
    if not token:
        return None

    model_name = os.getenv("HUGGINGFACE_REWRITE_MODEL", DEFAULT_REWRITE_MODEL)
    prompt_input = f"paraphrase: {text} </s>"

    payload = {
        "inputs": prompt_input,
        "parameters": {
            "max_length": max(50, int(len(text.split()) * 1.5)),
            "num_return_sequences": 1,
            "do_sample": False
        }
    }

    data, err = call_hf_api(model_name, payload, timeout=30)
    if not data or err:
        return None

    rewritten_text = ""
    if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
        rewritten_text = data[0]["generated_text"].strip()
    elif isinstance(data, dict) and "generated_text" in data:
        rewritten_text = data["generated_text"].strip()

    if not rewritten_text:
        return None

    # Clean any leftover prompt artifacts
    rewritten_text = re.sub(r'^(?:paraphrase:\s*)+', '', rewritten_text, flags=re.IGNORECASE).strip()

    orig_words = len(text.split())
    new_words = len(rewritten_text.split())

    return {
        "original_text": text,
        "rewritten_text": rewritten_text,
        "mode_used": mode,
        "original_word_count": orig_words,
        "rewritten_word_count": new_words,
        "word_diff": new_words - orig_words,
        "provider": "huggingface_transformer",
        "model": model_name,
        "notice": f"Neural paraphrase generated via Hugging Face T5 ({model_name})."
    }


# =====================================================================
# 7. Question Answering: deepset/roberta-base-squad2
# =====================================================================
def hf_answer_question(passage: str, question: str) -> Optional[Dict[str, Any]]:
    """Extract context-grounded answer spans using RoBERTa SQuAD2."""
    token = get_hf_token()
    if not token:
        return None

    model_name = os.getenv("HUGGINGFACE_QA_MODEL", DEFAULT_QA_MODEL)

    payload = {
        "inputs": {
            "question": question,
            "context": passage
        }
    }

    data, err = call_hf_api(model_name, payload, timeout=25)
    if not data or err or not isinstance(data, dict):
        return None

    answer = data.get("answer", "").strip()
    score = float(data.get("score", 0.0))
    start = int(data.get("start", 0))
    end = int(data.get("end", 0))

    # SQuAD 2.0 unanswerable threshold
    is_grounded = score >= 0.12 and bool(answer)
    if not is_grounded:
        return {
            "question": question,
            "answer": "Unable to determine answer from the provided passage. The reference context does not contain sufficient evidence.",
            "context": "",
            "confidence": round(score, 3),
            "confidence_label": "Unanswerable / Insufficient Evidence in Passage",
            "is_grounded": False,
            "span": {"start": 0, "end": 0},
            "provider": "huggingface_transformer",
            "model": model_name,
            "method": "RoBERTa-SQuAD2 Neural Span Reader with Abstention"
        }

    confidence_tier = "High Confidence" if score >= 0.60 else "Moderate Confidence" if score >= 0.30 else "Low / Tentative Match"

    return {
        "question": question,
        "answer": answer,
        "context": passage,
        "confidence": round(score, 3),
        "confidence_label": f"{confidence_tier} ({round(score * 100, 1)}%)",
        "is_grounded": True,
        "span": {
            "start": start,
            "end": end
        },
        "provider": "huggingface_transformer",
        "model": model_name,
        "method": "RoBERTa-SQuAD2 Neural Reading Comprehension"
    }
