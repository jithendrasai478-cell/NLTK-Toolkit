import json
from pathlib import Path
import pytest

def test_datasets_endpoint(client):
    """Verify that the datasets API endpoint reports >= 50 MB of genuine datasets."""
    res = client.get("/api/v1/datasets")
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["total_size_mb"] >= 50.0
    assert data["total_datasets"] >= 6
    dataset_names = [d["name"] for d in data["datasets"]]
    assert any("SQuAD" in name for name in dataset_names)
    assert any("20 Newsgroups" in name for name in dataset_names)
    assert any("SST-2" in name for name in dataset_names)

def test_models_status_endpoint(client):
    """Verify that the models status API endpoint reports trained model accuracy."""
    res = client.get("/api/v1/models/status")
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "topic_classification" in data
    assert "sentiment_analysis" in data
    assert "language_detection" in data
    assert data["topic_classification"]["accuracy"] >= 0.80
    assert data["sentiment_analysis"]["accuracy"] >= 0.70

def test_topic_classification_real_data(client):
    """Verify that the 20-Newsgroups-trained classifier correctly classifies news."""
    text = "NASA and SpaceX announce a joint orbital mission to explore lunar soil samples with robotic rovers."
    res = client.post("/api/v1/nlp/classify", json={"text": text})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["predicted_category"] == "Science & Health"
    assert data["confidence"] >= 0.70

def test_sentiment_dual_model(client):
    """Verify that sentiment returns both VADER and ML predictions."""
    text = "This machine learning toolkit is amazingly helpful and thoroughly enjoyable!"
    res = client.post("/api/v1/nlp/sentiment", json={"text": text})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["label"] == "Positive"
    assert "ml_sentiment" in data
    assert data["ml_sentiment"]["predicted_label"] == "positive"
    assert data["ml_sentiment"]["confidence"] >= 0.50

def test_qa_grounding_and_abstention(client):
    """Verify that QA answers answerable questions and abstains on unanswerable questions."""
    passage = "NLTK was created in 2001 by Steven Bird and Edward Loper at the University of Pennsylvania."
    
    # 1. Answerable
    res1 = client.post("/api/v1/nlp/qa", json={"passage": passage, "question": "When was NLTK created?"})
    assert res1.status_code == 200
    data1 = res1.get_json()["data"]
    assert "2001" in data1["answer"]
    assert data1["is_grounded"] is True

    # 2. Unanswerable
    res2 = client.post("/api/v1/nlp/qa", json={"passage": passage, "question": "What is the capital of Japan?"})
    assert res2.status_code == 200
    data2 = res2.get_json()["data"]
    assert data2["is_grounded"] is False
    assert "Unable to determine" in data2["answer"]

def test_telugu_stopwords_removal(client):
    """Verify that Telugu stopwords are filtered out using the IndicNLP collection."""
    telugu_text = "కంప్యూటర్ మరియు లాప్‌టాప్ చాలా ఉపయోగకరంగా ఉంటాయి."
    res = client.post("/api/v1/nlp/stopwords", json={"text": telugu_text, "options": {"language": "telugu"}})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["language_used"] == "telugu"
    assert any("మరియు" in s for s in data["removed_stopwords"]) or any("చాలా" in s for s in data["removed_stopwords"])

def test_multilingual_language_detection(client):
    """Verify that the character n-gram model identifies multiple languages."""
    res_te = client.post("/api/v1/nlp/language-detection", json={"text": "సహజ భాషా ప్రాసెసింగ్ అద్భుతమైనది."})
    assert res_te.get_json()["data"]["language_code"] == "te"

    res_fr = client.post("/api/v1/nlp/language-detection", json={"text": "Le traitement automatique du langage naturel est formidable."})
    assert res_fr.get_json()["data"]["language_code"] == "fr"
