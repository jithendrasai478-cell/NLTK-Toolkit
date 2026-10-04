import pytest
from backend.services.classifier_service import (
    classify_text,
    compute_exact_percentages,
    get_classifier_diagnostics,
    get_or_load_model,
    NEWSGROUPS_TO_TOPIC_MAP,
)

def test_pipeline_attributes_and_truthfulness():
    """Verify that the model pipeline is real, trained, and truthfully described."""
    pipeline = get_or_load_model()
    tfidf = pipeline.named_steps["tfidf"]
    clf = pipeline.named_steps["clf"]

    # Model type and classes
    assert clf.__class__.__name__ == "LogisticRegression"
    assert tfidf.__class__.__name__ == "TfidfVectorizer"
    assert len(clf.classes_) == 6
    expected_classes = sorted(["Business", "Entertainment", "Politics", "Science & Health", "Sports", "Technology"])
    assert sorted(clf.classes_) == expected_classes
    assert len(tfidf.vocabulary_) == 15000

    # Verify 20 newsgroups mapping
    assert len(NEWSGROUPS_TO_TOPIC_MAP) == 20
    mapped_categories = set(NEWSGROUPS_TO_TOPIC_MAP.values())
    assert mapped_categories == set(clf.classes_)


def test_compute_exact_percentages_sums_to_100():
    """Verify that the Largest Remainder Method guarantees exact 100.0% totals."""
    # Test with the exact Tesla example probabilities
    tesla_probs = [0.389445, 0.349784, 0.094771, 0.059435, 0.059253, 0.047311]
    pcts = compute_exact_percentages(tesla_probs, precision=1)
    assert sum(pcts) == 100.0
    assert pcts == [39.0, 35.0, 9.5, 5.9, 5.9, 4.7]

    # Test uniform distribution
    uniform = [1 / 6] * 6
    u_pcts = compute_exact_percentages(uniform, precision=1)
    assert sum(u_pcts) == 100.0

    # Test edge cases
    single_class = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    s_pcts = compute_exact_percentages(single_class, precision=1)
    assert sum(s_pcts) == 100.0
    assert s_pcts[0] == 100.0


def test_tesla_exact_input():
    """
    Test the exact Tesla prompt input:
    'Tesla announces new autonomous driving neural network architecture with end-to-end vision processing.'
    Verifies:
    - Real pipeline output (no fake hardcoded numbers)
    - Predicted category is Technology
    - Sports is runner-up due to rec.autos mapping in 20 Newsgroups
    - Percentages sum to exactly 100.0%
    - Confidence tier is Moderate
    """
    text = "Tesla announces new autonomous driving neural network architecture with end-to-end vision processing."
    result = classify_text(text)

    assert result["predicted_category"] == "Technology"
    assert result["confidence_tier"] == "Moderate"
    assert 0.35 <= result["confidence"] <= 0.45
    assert result["is_out_of_domain"] is False

    probs = result["category_probabilities"]
    assert len(probs) == 6
    assert probs[0]["category"] == "Technology"
    assert probs[1]["category"] == "Sports"

    # Strict check: Displayed percentages must sum to exactly 100.0%
    total_pct = sum(p["percentage"] for p in probs)
    assert total_pct == 100.0

    # Verify descending sort
    for i in range(len(probs) - 1):
        assert probs[i]["confidence"] >= probs[i + 1]["confidence"]
        assert probs[i]["percentage"] >= probs[i + 1]["percentage"]


def test_required_unrelated_examples():
    """
    Test the prompt's required test inputs across multiple categories.
    Verifies that the model dynamically predicts results through the ML pipeline.
    """
    # 1. Technology
    tech_res = classify_text("Tesla announces a new autonomous driving neural network architecture.")
    assert tech_res["predicted_category"] == "Technology"
    assert sum(p["percentage"] for p in tech_res["category_probabilities"]) == 100.0

    # 2. Sports
    sports_res = classify_text("The football team won the championship after scoring two goals.")
    assert sports_res["predicted_category"] == "Sports"
    assert sports_res["confidence_tier"] == "High"
    assert sports_res["confidence"] > 0.80
    assert sum(p["percentage"] for p in sports_res["category_probabilities"]) == 100.0

    # 3. Science
    sci_res = classify_text("Researchers developed a new method for studying biological cells.")
    assert sci_res["predicted_category"] == "Science & Health"
    assert sum(p["percentage"] for p in sci_res["category_probabilities"]) == 100.0

    # 4. Politics
    pol_res = classify_text("The government announced a new election policy.")
    assert pol_res["predicted_category"] == "Politics"
    assert sum(p["percentage"] for p in pol_res["category_probabilities"]) == 100.0

    # 5. Business & Entertainment (documents behavior on 20 Newsgroups domain limitations)
    biz_res = classify_text("The company reported increased quarterly revenue and profits.")
    assert sum(p["percentage"] for p in biz_res["category_probabilities"]) == 100.0
    assert biz_res["confidence_tier"] in ("Low", "Moderate")

    ent_res = classify_text("The film received several awards at the international festival.")
    assert sum(p["percentage"] for p in ent_res["category_probabilities"]) == 100.0
    assert ent_res["confidence_tier"] in ("Low", "Moderate")


def test_short_inputs_handling():
    """
    Test very short inputs to ensure no crashes or invalid output:
    - 'Tesla autonomous driving technology'
    - 'Football championship results'
    - 'Stock market investment strategy'
    - 'Python machine learning tutorial'
    - 'Political election campaign'
    """
    short_inputs = [
        "Tesla autonomous driving technology",
        "Football championship results",
        "Stock market investment strategy",
        "Python machine learning tutorial",
        "Political election campaign",
    ]
    for text in short_inputs:
        res = classify_text(text)
        assert res["predicted_category"] in ["Business", "Entertainment", "Politics", "Science & Health", "Sports", "Technology"]
        assert len(res["category_probabilities"]) == 6
        assert sum(p["percentage"] for p in res["category_probabilities"]) == 100.0
        assert res["confidence"] > 0.0


def test_out_of_domain_and_ambiguous_inputs():
    """Verify that out-of-domain and ambiguous inputs are transparently flagged."""
    # Completely out-of-vocabulary gibberish
    gibberish = "qwertyuiop asdfghjkl zxcvbnm"
    res_ood = classify_text(gibberish)
    assert res_ood["is_out_of_domain"] is True
    assert res_ood["vocab_tokens_matched"] == 0
    assert res_ood["confidence_tier"] == "Low"
    assert res_ood["warning"] is not None
    assert sum(p["percentage"] for p in res_ood["category_probabilities"]) == 100.0

    # Ambiguous stopwords-only input
    stopwords = "the and of in a to"
    res_amb = classify_text(stopwords)
    assert res_amb["confidence_tier"] == "Low"
    assert sum(p["percentage"] for p in res_amb["category_probabilities"]) == 100.0


def test_diagnostics_and_evaluation_endpoint(client):
    """Verify that diagnostics exposes real held-out evaluation metrics and model specs."""
    res = client.get("/api/v1/nlp/classify/diagnostics")
    assert res.status_code == 200
    data = res.get_json()["data"]

    assert data["model_type"] == "LogisticRegression"
    assert data["vectorizer_type"] == "TfidfVectorizer"
    assert data["vocabulary_size"] == 15000
    assert data["num_classes"] == 6
    assert data["training_samples"] == 12521
    assert data["test_samples"] == 2600
    assert data["evaluation"]["test_accuracy"] == 0.8765
    assert data["evaluation"]["macro_f1"] == 0.8549
    assert "20 Newsgroups mapped to 6 application topics" in data["description"]


def test_empty_input_error_handling(client):
    """Verify that empty inputs produce proper 400 errors instead of fake results."""
    res = client.post("/api/v1/nlp/classify", json={"text": "   "})
    assert res.status_code == 400
    body = res.get_json()
    assert body["success"] is False
    assert body["error"]["code"] == "EMPTY_INPUT"
