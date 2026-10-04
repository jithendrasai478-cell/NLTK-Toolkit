import pytest

def test_tokenize_endpoint(client):
    res = client.post("/api/v1/nlp/tokenize", json={"text": "Natural Language Processing is amazing! It works."})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["sentence_count"] == 2
    assert data["token_count"] > 5
    assert "tokens" in data

def test_tokenize_telugu_text(client):
    telugu_text = "సహజ భాషా ప్రాసెసింగ్ అద్భుతమైనది. ఇది నిజంగా పనిచేస్తుంది."
    res = client.post("/api/v1/nlp/tokenize", json={"text": telugu_text})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["character_count"] > 10
    assert len(data["tokens"]) > 3

def test_sentiment_endpoint(client):
    res = client.post("/api/v1/nlp/sentiment", json={"text": "The NLTK toolkit is fantastic and wonderful!"})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["label"] == "Positive"
    assert data["scores"]["compound"] > 0.4

def test_sentiment_negative(client):
    res = client.post("/api/v1/nlp/sentiment", json={"text": "This application failed terribly and was awful."})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["label"] == "Negative"
    assert data["scores"]["compound"] < -0.4

def test_summarize_endpoint(client):
    article = (
        "Natural language processing is an interdisciplinary subfield of linguistics, computer science, and AI. "
        "It focuses on the interactions between human language and computational algorithms. "
        "Modern NLP combines computational linguistics with deep learning models. "
        "These technologies enable computers to process human language in the form of text or voice data. "
        "Its applications include sentiment analysis, machine translation, and speech recognition."
    )
    res = client.post("/api/v1/nlp/summarize", json={"text": article, "options": {"summary_length": "short"}})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "summary" in data
    assert data["summary_sentence_count"] < data["original_sentence_count"]
    assert data["compression_ratio"] < 1.0

def test_keywords_endpoint(client):
    text = "Machine learning algorithms analyze large text corpora to extract meaningful patterns and linguistic structures."
    res = client.post("/api/v1/nlp/keywords", json={"text": text, "options": {"top_n": 6, "method": "tfidf"}})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert len(data["keywords"]) == 6
    assert "rank" in data["keywords"][0]
    assert data["keywords"][0]["score"] == 0.2085
    assert any(k["type"] == "keyphrase" for k in data["keywords"])
    assert any(k["type"] == "keyword" for k in data["keywords"])
    assert "debug" in data
    assert data["debug"]["total_features_found"] == 23
    assert len(data["debug"]["raw_scores_before_filtering"]) == 23

def test_keywords_multidoc_corpus_endpoint(client):
    text = "Machine learning algorithms analyze large text corpora to extract meaningful patterns and linguistic structures."
    res = client.post("/api/v1/nlp/keywords", json={
        "text": text,
        "options": {
            "top_n": 10,
            "method": "tfidf",
            "corpus_mode": "multi_doc"
        }
    })
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["corpus_mode"] == "multi_doc"
    assert data["debug"]["corpus_size"] == 6
    # Verify that weights naturally vary based on genuine document frequency
    scores = [k["score"] for k in data["keywords"]]
    assert len(set(scores)) > 1  # Demonstrates different weights!
    # Common terms like 'algorithms' appear in multiple reference docs and should have lower IDF and score
    # Unique keyphrases like 'linguistic structures' or 'extract meaningful' appear in only 1 doc and should have higher score
    top_terms = [k["keyword"] for k in data["keywords"][:5]]
    assert any("linguistic" in t or "extract" in t for t in top_terms)
    # Check that doc_frequency and idf are returned in debug and keywords
    assert "doc_frequency" in data["keywords"][0]
    assert "idf" in data["keywords"][0]

def test_keywords_custom_reference_corpus(client):
    text = "Machine learning algorithms analyze large text corpora to extract meaningful patterns and linguistic structures."
    custom_corpus = [
        "Machine learning is widely used.",
        "Linguistic structures are very rare in general text."
    ]
    res = client.post("/api/v1/nlp/keywords", json={
        "text": text,
        "options": {
            "top_n": 5,
            "method": "tfidf",
            "corpus_mode": "multi_doc",
            "reference_corpus": custom_corpus
        }
    })
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["corpus_mode"] == "multi_doc"
    assert data["debug"]["corpus_size"] == 3
    assert data["debug"]["reference_documents_count"] == 2



def test_classify_endpoint(client):
    tech_text = "Python programmers build web servers and neural network algorithms on cloud computers."
    res = client.post("/api/v1/nlp/classify", json={"text": tech_text})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["predicted_category"] == "Technology"
    assert data["confidence"] > 0.2

def test_translate_endpoint(client):
    res = client.post("/api/v1/nlp/translate", json={
        "text": "Natural Language Processing is amazing!",
        "source_language": "en",
        "target_language": "te"
    })
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "translated_text" in data
    assert data["target_language"] == "te"

def test_languages_endpoint(client):
    res = client.get("/api/v1/languages")
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["total_languages"] >= 10
    codes = [item["code"] for item in data["supported_languages"]]
    assert "te" in codes
    assert "hi" in codes
    assert "en" in codes

def test_rewrite_endpoint(client):
    res = client.post("/api/v1/nlp/rewrite", json={
        "text": "The kids will purchase big computers to commence work.",
        "options": {"mode": "formal"}
    })
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "children" in data["rewritten_text"].lower()

def test_qa_endpoint(client):
    passage = "NLTK was created in 2001 by Steven Bird and Edward Loper at the University of Pennsylvania."
    question = "When was NLTK created?"
    res = client.post("/api/v1/nlp/qa", json={"passage": passage, "question": question})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "2001" in data["answer"]
    assert data["confidence"] > 0.0

def test_ner_endpoint(client):
    text = "Sundar Pichai works at Google in California."
    res = client.post("/api/v1/nlp/ner", json={"text": text})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "entities" in data
    assert len(data["entities"]) > 0

def test_statistics_endpoint(client):
    text = "Simple tools. Powerful features. Built for learners, researchers and developers."
    res = client.post("/api/v1/nlp/statistics", json={"text": text})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["word_count"] > 5
    assert data["sentence_count"] == 3
    assert "estimated_reading_time" in data

def test_stopwords_endpoint(client):
    text = "This is a great demonstration of removing stop words from text."
    res = client.post("/api/v1/nlp/stopwords", json={"text": text})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["removed_count"] > 0
    assert "this" in data["removed_stopwords"]

def test_stem_endpoint(client):
    text = "processing computational algorithms studied"
    res = client.post("/api/v1/nlp/stem", json={"text": text})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert len(data["stems"]) == 4

def test_lemmatize_endpoint(client):
    text = "The corpora contained better running feet"
    res = client.post("/api/v1/nlp/lemmatize", json={"text": text})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert len(data["lemmas"]) > 0

def test_pos_tag_endpoint(client):
    text = "Natural Language Processing is amazing!"
    res = client.post("/api/v1/nlp/pos-tag", json={"text": text})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert len(data["tagged_tokens"]) > 3

def test_ngrams_endpoint(client):
    text = "Deep learning and natural language processing"
    res = client.post("/api/v1/nlp/ngrams", json={"text": text, "options": {"n": 2}})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["n"] == 2
    assert len(data["ngrams"]) > 0

def test_word_frequency_endpoint(client):
    text = "python python language python nlp language processing"
    res = client.post("/api/v1/nlp/word-frequency", json={"text": text})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["distribution"][0]["word"] == "python"
    assert data["distribution"][0]["count"] == 3

def test_language_detection_endpoint(client):
    telugu_text = "నమస్కారం, మీరు ఎలా ఉన్నారు?"
    res = client.post("/api/v1/nlp/language-detection", json={"text": telugu_text})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["language_code"] == "te"

def test_similarity_endpoint(client):
    t1 = "Machine learning and artificial intelligence algorithms."
    t2 = "Artificial intelligence and machine learning software models."
    res = client.post("/api/v1/nlp/similarity", json={"text1": t1, "text2": t2})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["similarity_score"] > 0.4
    assert len(data["shared_terms"]) >= 3

def test_validation_empty_text(client):
    res = client.post("/api/v1/nlp/sentiment", json={"text": "   "})
    assert res.status_code == 400
    err = res.get_json()["error"]
    assert err["code"] == "EMPTY_INPUT"

def test_validation_missing_field(client):
    res = client.post("/api/v1/nlp/summarize", json={})
    assert res.status_code == 400
    err = res.get_json()["error"]
    assert err["code"] == "MISSING_FIELD"
