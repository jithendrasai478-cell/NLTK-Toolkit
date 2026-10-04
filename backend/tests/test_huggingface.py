import os
from pathlib import Path
import pytest
from backend.providers.huggingface_provider import (
    get_hf_token, 
    hf_summarize_text, 
    hf_translate_text, 
    hf_answer_question,
    NLLB_LANGUAGE_MAP
)
from backend.services.summarizer_service import summarize_text
from backend.services.translator_service import translate_text
from backend.services.qa_service import answer_question

def test_hf_token_configured():
    """Verify that the Hugging Face token is loaded from environment."""
    token = get_hf_token()
    if not token or token.startswith("YOUR_"):
        pytest.skip("Hugging Face API key is a placeholder or not configured")
    assert token.startswith("hf_")

def test_hf_language_mappings():
    """Verify that NLLB-200 supports Telugu and Indic language codes."""
    assert NLLB_LANGUAGE_MAP["te"] == "tel_Telu"
    assert NLLB_LANGUAGE_MAP["hi"] == "hin_Deva"
    assert NLLB_LANGUAGE_MAP["ta"] == "tam_Taml"
    assert NLLB_LANGUAGE_MAP["en"] == "eng_Latn"

def test_summarize_fallback_and_execution(client):
    """Verify that summarization succeeds whether HF or local fallback is used."""
    text = (
        "Natural language processing is an interdisciplinary subfield of computer science "
        "and artificial intelligence. It is primarily concerned with providing computers the "
        "ability to read, understand and derive meaning from human languages in a valuable manner."
    )
    res = client.post("/api/v1/nlp/summarize", json={"text": text})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "summary" in data
    assert len(data["summary"]) > 10
    assert "provider" in data

def test_translation_fallback_and_execution(client):
    """Verify that translation succeeds across English to Telugu."""
    text = "Hello world"
    res = client.post("/api/v1/nlp/translate", json={"text": text, "source_language": "en", "target_language": "te"})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "translated_text" in data
    assert len(data["translated_text"]) > 0

def test_qa_fallback_and_execution(client):
    """Verify that QA answers correctly with span and grounding."""
    passage = "NLTK was created in 2001 by Steven Bird and Edward Loper at the University of Pennsylvania."
    res = client.post("/api/v1/nlp/qa", json={"passage": passage, "question": "When was NLTK created?"})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "2001" in data["answer"]
    assert data["is_grounded"] is True

def test_hf_datasets_exist():
    """Verify that the Hugging Face dataset files exist on disk for all 8 features."""
    base_data = Path(__file__).resolve().parent.parent / "data" / "raw"
    # 1. Summarization
    assert (base_data / "summarization" / "hf_xsum_summaries.jsonl").exists()
    assert (base_data / "summarization" / "cnn_dailymail_samples.jsonl").exists()
    # 2. Sentiment
    assert (base_data / "sentiment" / "imdb_sentiment.jsonl").exists()
    assert (base_data / "sentiment" / "go_emotions.jsonl").exists()
    # 3. Keywords
    assert (base_data / "keywords" / "inspec_keyphrases.jsonl").exists()
    # 4. Classification
    assert (base_data / "classification" / "ag_news.jsonl").exists()
    assert (base_data / "classification" / "banking77_intents.jsonl").exists()
    # 5. NER
    assert (base_data / "ner" / "conll2003_entities.jsonl").exists()
    # 6. Translation
    assert (base_data / "translation" / "hf_opus_english_telugu.jsonl").exists()
    assert (base_data / "translation" / "flores200_benchmark.jsonl").exists()
    # 7. Rewrite
    assert (base_data / "rewrite" / "paws_paraphrases.jsonl").exists()
    # 8. Q&A
    assert (base_data / "qa" / "hf_squad_v2_samples.jsonl").exists()
    assert (base_data / "qa" / "natural_questions_samples.jsonl").exists()

def test_hf_ner_endpoint(client):
    """Verify that NER extraction operates cleanly with CoNLL/BERT models."""
    text = "Steven Bird and Edward Loper developed NLTK in Philadelphia."
    res = client.post("/api/v1/nlp/ner", json={"text": text})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "entities" in data
    assert data["total_entities_found"] >= 1

def test_hf_rewrite_paraphrase(client):
    """Verify that paraphrase rewriting functions seamlessly."""
    text = "We must utilize modern algorithms to maximize computational efficiency."
    res = client.post("/api/v1/nlp/rewrite", json={"text": text, "options": {"mode": "paraphrase"}})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "rewritten_text" in data
    assert len(data["rewritten_text"]) > 10
