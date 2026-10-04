import os
import re
from pathlib import Path
from typing import Any, Dict
import joblib
from nltk.sentiment.vader import SentimentIntensityAnalyzer

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "data" / "models" / "sentiment_classifier.joblib"

_ml_pipeline = None

def get_ml_sentiment_model():
    global _ml_pipeline
    if _ml_pipeline is None and MODEL_PATH.exists():
        try:
            _ml_pipeline = joblib.load(MODEL_PATH)
        except Exception:
            _ml_pipeline = None
    return _ml_pipeline

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Perform hybrid sentiment analysis using both:
    1. NLTK VADER Rule-Based Lexicon Intensity Analyzer
    2. Supervised ML Classifier trained on Stanford Sentiment Treebank (SST-2)
    Provides transparent confidence metrics and script-aware warnings.
    """
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]

    # 1. VADER Lexicon Sentiment
    if compound >= 0.05:
        sentiment_label = "Positive"
        sentiment_tone = "Optimistic, Favorable, or Enthusiastic"
        color = "emerald"
    elif compound <= -0.05:
        sentiment_label = "Negative"
        sentiment_tone = "Critical, Concerned, or Dissatisfied"
        color = "rose"
    else:
        sentiment_label = "Neutral"
        sentiment_tone = "Objective, Informational, or Matter-of-Fact"
        color = "amber"

    # 2. Machine Learning Classifier (SST-2 Model)
    ml_result = None
    pipeline = get_ml_sentiment_model()
    if pipeline:
        try:
            pred_label = str(pipeline.predict([text])[0])
            probs = pipeline.predict_proba([text])[0]
            classes = [str(c) for c in pipeline.classes_]
            prob_dict = {cls: round(float(p), 4) for cls, p in zip(classes, probs)}
            ml_result = {
                "predicted_label": pred_label,
                "confidence": round(float(max(probs)), 4),
                "probabilities": prob_dict,
                "model": "TF-IDF + Logistic Regression (SST-2 Benchmark)"
            }
        except Exception:
            ml_result = None

    # 3. Hugging Face Transformer Sentiment (DistilBERT SST-2)
    hf_result = None
    try:
        from backend.providers.huggingface_provider import hf_analyze_sentiment
        hf_result = hf_analyze_sentiment(text)
    except Exception:
        hf_result = None

    # 3. Check for Telugu / Non-Latin Indian Scripts
    is_telugu = bool(re.search(r'[\u0C00-\u0C7F]', text))
    is_indic = bool(re.search(r'[\u0900-\u0D7F]', text))

    disclaimer = (
        "Sentiment analysis is an algorithmic estimate based on vocabulary intensity and statistical training."
    )
    if is_telugu:
        disclaimer = (
            "NOTICE: Telugu script detected. NLTK VADER operates on an English social lexicon; "
            "scores for native Telugu text reflect zero English sentiment words."
        )
    elif is_indic:
        disclaimer = (
            "NOTICE: Non-Latin Indic script detected. Standard VADER lexicon is English-calibrated."
        )

    return {
        "label": sentiment_label,
        "tone": sentiment_tone,
        "color": color,
        "scores": {
            "compound": compound,
            "positive": scores["pos"],
            "negative": scores["neg"],
            "neutral": scores["neu"]
        },
        "score_percentages": {
            "positive": round(scores["pos"] * 100, 1),
            "negative": round(scores["neg"] * 100, 1),
            "neutral": round(scores["neu"] * 100, 1)
        },
        "ml_sentiment": ml_result,
        "transformer_sentiment": hf_result,
        "explanation": {
            "compound_range": "-1.0 (extremely negative) to +1.0 (extremely positive)",
            "interpretation": f"Compound score of {compound:+.3f} indicates {sentiment_label.lower()} sentiment.",
            "disclaimer": disclaimer
        }
    }
