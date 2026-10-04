import pytest
from backend.services.rewriter_service import count_words, has_negation, extract_numbers

TEST_SENTENCES = [
    ("problem", "It is imperative that we utilize all available algorithmic methodologies to optimize computational throughput."),
    ("simple", "The weather is very pleasant today."),
    ("formal_academic", "Machine learning algorithms are utilized to analyze large datasets."),
    ("informal", "I think we should fix this problem as soon as possible."),
    ("long", "The system processes large amounts of textual information in order to identify meaningful patterns and generate useful results."),
    ("technical", "The server processes incoming requests using an asynchronous event-driven architecture."),
    ("numbers", "The system processed 10,000 documents in approximately 25 minutes."),
    ("negative", "The system does not support offline processing."),
]

ALL_MODES = ["simplify", "formal", "informal", "shorten", "expand", "paraphrase"]

def test_all_six_modes_on_problem_sentence(client):
    """Verify that all six modes on the problem sentence produce genuine, validated transformations."""
    sent = "It is imperative that we utilize all available algorithmic methodologies to optimize computational throughput."
    
    # 1. SIMPLIFY
    res = client.post("/api/v1/nlp/rewrite", json={"text": sent, "options": {"mode": "simplify"}})
    assert res.status_code == 200
    d = res.get_json()["data"]
    assert "use" in d["rewritten_text"].lower()
    assert "methods" in d["rewritten_text"].lower()
    assert d["rewritten_word_count"] <= d["original_word_count"]
    assert "uncommitted" not in d["rewritten_text"].lower()

    # 2. FORMAL
    res = client.post("/api/v1/nlp/rewrite", json={"text": sent, "options": {"mode": "formal"}})
    assert res.status_code == 200
    d = res.get_json()["data"]
    assert len(d["rewritten_text"]) > 10

    # 3. INFORMAL
    res = client.post("/api/v1/nlp/rewrite", json={"text": sent, "options": {"mode": "informal"}})
    assert res.status_code == 200
    d = res.get_json()["data"]
    assert "really need to" in d["rewritten_text"].lower()

    # 4. SHORTEN
    res = client.post("/api/v1/nlp/rewrite", json={"text": sent, "options": {"mode": "shorten"}})
    assert res.status_code == 200
    d = res.get_json()["data"]
    assert d["rewritten_word_count"] < d["original_word_count"]
    assert d["word_diff"] < 0
    assert "available" in d["rewritten_text"].lower()
    assert "optimize" in d["rewritten_text"].lower()
    assert "maximize" not in d["rewritten_text"].lower()

    # 5. EXPAND
    res = client.post("/api/v1/nlp/rewrite", json={"text": sent, "options": {"mode": "expand"}})
    assert res.status_code == 200
    d = res.get_json()["data"]
    assert d["rewritten_word_count"] > d["original_word_count"]
    assert d["word_diff"] > 0
    # Verify no tautological redundancy or unsupported external assumptions
    assert "critically important and imperative" not in d["rewritten_text"].lower()
    assert "throughput and performance" not in d["rewritten_text"].lower()
    assert "across the system" not in d["rewritten_text"].lower()

    # 6. PARAPHRASE
    res = client.post("/api/v1/nlp/rewrite", json={"text": sent, "options": {"mode": "paraphrase"}})
    assert res.status_code == 200
    d = res.get_json()["data"]
    assert d["rewritten_text"].lower() != sent.lower()
    assert "uncommitted" not in d["rewritten_text"].lower()
    assert "optimize" in d["rewritten_text"].lower()
    assert "maximize" not in d["rewritten_text"].lower()

def test_benchmark_sentences_all_modes(client):
    """Test all benchmark sentences A-G across all 6 modes."""
    for label, sent in TEST_SENTENCES:
        for mode in ALL_MODES:
            res = client.post("/api/v1/nlp/rewrite", json={"text": sent, "options": {"mode": mode}})
            assert res.status_code == 200, f"Failed for {label} in mode {mode}"
            d = res.get_json()["data"]
            assert bool(d["rewritten_text"]), f"Empty output for {label} in mode {mode}"
            assert d["original_word_count"] == count_words(sent)
            assert d["rewritten_word_count"] == count_words(d["rewritten_text"])
            assert d["word_diff"] == d["rewritten_word_count"] - d["original_word_count"]
            assert "WordNet" not in d["notice"]

def test_semantic_preservation_negation(client):
    """Verify that negation is strictly preserved in all modes."""
    sent = "The system does not support offline processing."
    for mode in ALL_MODES:
        res = client.post("/api/v1/nlp/rewrite", json={"text": sent, "options": {"mode": mode}})
        assert res.status_code == 200
        d = res.get_json()["data"]
        assert has_negation(d["rewritten_text"]), f"Negation lost in mode {mode}: {d['rewritten_text']}"

def test_semantic_preservation_numbers(client):
    """Verify that numbers (10,000 and 25) are strictly preserved in all modes."""
    sent = "The system processed 10,000 documents in approximately 25 minutes."
    for mode in ALL_MODES:
        res = client.post("/api/v1/nlp/rewrite", json={"text": sent, "options": {"mode": mode}})
        assert res.status_code == 200
        d = res.get_json()["data"]
        nums = extract_numbers(d["rewritten_text"])
        assert "10,000" in nums or "10000" in nums, f"Number 10,000 lost in mode {mode}"
        assert "25" in nums, f"Number 25 lost in mode {mode}"

def test_shorten_is_strictly_shorter(client):
    """Verify that shorten produces fewer words on sentences longer than 2 words."""
    for label, sent in TEST_SENTENCES:
        res = client.post("/api/v1/nlp/rewrite", json={"text": sent, "options": {"mode": "shorten"}})
        assert res.status_code == 200
        d = res.get_json()["data"]
        assert d["rewritten_word_count"] < d["original_word_count"], f"Shorten failed to reduce length on {label}: {d['original_word_count']} -> {d['rewritten_word_count']}"

def test_expand_is_strictly_longer(client):
    """Verify that expand produces more words on all benchmark sentences."""
    for label, sent in TEST_SENTENCES:
        res = client.post("/api/v1/nlp/rewrite", json={"text": sent, "options": {"mode": "expand"}})
        assert res.status_code == 200
        d = res.get_json()["data"]
        assert d["rewritten_word_count"] > d["original_word_count"], f"Expand failed to increase length on {label}: {d['original_word_count']} -> {d['rewritten_word_count']}"

def test_paraphrase_is_different_and_meaningful(client):
    """Verify that paraphrase alters wording/structure without distortion."""
    for label, sent in TEST_SENTENCES:
        res = client.post("/api/v1/nlp/rewrite", json={"text": sent, "options": {"mode": "paraphrase"}})
        assert res.status_code == 200
        d = res.get_json()["data"]
        assert d["rewritten_text"].strip().lower() != sent.strip().lower()

def test_multi_sentence_handling(client):
    """Verify that multi-sentence input is cleanly tokenized, transformed, and joined."""
    text = "The weather is very pleasant today. We should fix this problem as soon as possible."
    res = client.post("/api/v1/nlp/rewrite", json={"text": text, "options": {"mode": "simplify"}})
    assert res.status_code == 200
    d = res.get_json()["data"]
    assert "promptly" in d["rewritten_text"] or "pleasant" in d["rewritten_text"]
    assert d["original_word_count"] == count_words(text)
    assert d["rewritten_word_count"] == count_words(d["rewritten_text"])

def test_empty_and_short_input(client):
    """Verify safe behavior for empty and short input."""
    # Empty input via API is caught by validator with 400 EMPTY_INPUT
    res = client.post("/api/v1/nlp/rewrite", json={"text": "   ", "options": {"mode": "simplify"}})
    assert res.status_code == 400
    assert "EMPTY_INPUT" in res.get_json()["error"]["code"]

    # Direct service call handles empty string safely
    from backend.services.rewriter_service import rewrite_text
    d = rewrite_text("", mode="simplify")
    assert d["original_word_count"] == 0
    assert d["rewritten_word_count"] == 0
    assert d["rewritten_text"] == ""

    # Short single word via API
    res = client.post("/api/v1/nlp/rewrite", json={"text": "Proceed.", "options": {"mode": "simplify"}})
    assert res.status_code == 200
    d = res.get_json()["data"]
    assert d["original_word_count"] == 1
    assert len(d["rewritten_text"]) > 0

def test_invalid_mode_error(client):
    """Verify that invalid mode returns 400 error."""
    res = client.post("/api/v1/nlp/rewrite", json={"text": "Test input.", "options": {"mode": "invalid_mode_xyz"}})
    assert res.status_code == 400
