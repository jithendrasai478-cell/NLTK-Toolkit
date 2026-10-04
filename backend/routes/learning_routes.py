from typing import Any, Dict, List
from flask import Blueprint
from backend.utils.error_handlers import api_success, APIException

learning_bp = Blueprint("learning", __name__, url_prefix="/api/v1/learning")

TOPICS: List[Dict[str, Any]] = [
    {
        "id": "what-is-nlp",
        "title": "What is Natural Language Processing (NLP)?",
        "definition": "NLP is an interdisciplinary branch of artificial intelligence and computer science focused on enabling computers to understand, interpret, and generate human language.",
        "why_useful": "Human communication is unstructured and ambiguous. NLP unlocks actionable intelligence from millions of articles, emails, reviews, and documents.",
        "python_example": "text = 'NLP is awesome!'\nprint(text.lower().split())",
        "expected_output": "['nlp', 'is', 'awesome!']",
        "common_mistakes": "Assuming simple string matching is equivalent to understanding syntax, context, and semantics."
    },
    {
        "id": "tokenization",
        "title": "Text Tokenization",
        "definition": "The process of splitting a stream of textual data into smaller discrete linguistic units such as words, punctuation marks, or sentences.",
        "why_useful": "Tokenization forms the foundational first step of almost every NLP pipeline before tagging, indexing, or model inference.",
        "python_example": "import nltk\nfrom nltk.tokenize import word_tokenize\ntext = 'Natural Language Processing is amazing!'\nprint(word_tokenize(text))",
        "expected_output": "['Natural', 'Language', 'Processing', 'is', 'amazing', '!']",
        "common_mistakes": "Using standard whitespace splitting (`text.split()`) which erroneously attaches punctuation symbols to adjacent words."
    },
    {
        "id": "sentiment-analysis",
        "title": "Sentiment Analysis & VADER",
        "definition": "The computational study of opinions, sentiments, evaluations, attitudes, and emotions expressed in text.",
        "why_useful": "Allows automated monitoring of brand reputation, customer feedback reviews, and market sentiment trends.",
        "python_example": "from nltk.sentiment.vader import SentimentIntensityAnalyzer\nsia = SentimentIntensityAnalyzer()\nprint(sia.polarity_scores('The NLTK toolkit is fantastic!'))",
        "expected_output": "{'neg': 0.0, 'neu': 0.385, 'pos': 0.615, 'compound': 0.6239}",
        "common_mistakes": "Treating polarity scores as verified psychological truths rather than vocabulary-based sentiment intensity estimates."
    },
    {
        "id": "extractive-summarization",
        "title": "Extractive Text Summarization",
        "definition": "A summarization technique that scores and ranks existing sentences from the original document and outputs the top sentences verbatim.",
        "why_useful": "Guarantees factual accuracy because no new statements or ungrounded claims are hallucinated.",
        "python_example": "import nltk\nfrom collections import Counter\nsentences = nltk.sent_tokenize('NLP is great. It helps computers learn. Humans love it.')\nprint(sentences[0])",
        "expected_output": "'NLP is great.'",
        "common_mistakes": "Confusing extractive summarization (verbatim selection) with abstractive summarization (generative rephrasing)."
    },
    {
        "id": "stemming-vs-lemmatization",
        "title": "Stemming vs. Lemmatization",
        "definition": "Stemming slices off word suffixes heuristically, while lemmatization uses vocabulary and morphological rules to find legitimate dictionary lemmas.",
        "why_useful": "Normalizes inflected word variants ('running', 'runs', 'ran') to standard roots to consolidate vocabulary size.",
        "python_example": "from nltk.stem import PorterStemmer, WordNetLemmatizer\nps = PorterStemmer()\nwnl = WordNetLemmatizer()\nprint('Stem of studies:', ps.stem('studies'))\nprint('Lemma of studies:', wnl.lemmatize('studies'))",
        "expected_output": "Stem of studies: studi\nLemma of studies: study",
        "common_mistakes": "Expecting stemming to always produce valid dictionary words."
    },
    {
        "id": "pos-tagging",
        "title": "Part-of-Speech (POS) Tagging",
        "definition": "Assigning grammatical markers (Noun, Verb, Adjective, Adverb, Preposition) to each token in a sentence based on syntax and context.",
        "why_useful": "Crucial for syntactic parsing, named entity extraction, and disambiguating word senses (e.g. 'book a flight' vs 'read a book').",
        "python_example": "import nltk\ntokens = nltk.word_tokenize('Computers process language.')\nprint(nltk.pos_tag(tokens))",
        "expected_output": "[('Computers', 'NNS'), ('process', 'VBP'), ('language', 'NN'), ('.', '.')]",
        "common_mistakes": "Assuming a word always has one fixed POS tag regardless of syntactic context."
    },
    {
        "id": "tf-idf",
        "title": "Term Frequency - Inverse Document Frequency (TF-IDF)",
        "definition": "A mathematical weighting method measuring how important a word is to a document relative to a broader collection (corpus).",
        "why_useful": "Downweights universally common words like 'the' and 'is' while elevating distinctive domain terms.",
        "python_example": "from sklearn.feature_extraction.text import TfidfVectorizer\nvec = TfidfVectorizer()\nX = vec.fit_transform(['Python is great', 'Python web server'])\nprint(vec.get_feature_names_out())",
        "expected_output": "['great' 'is' 'python' 'server' 'web']",
        "common_mistakes": "Applying TF-IDF on tiny single-sentence snippets where document frequency has no comparative distribution."
    },
    {
        "id": "named-entity-recognition",
        "title": "Named Entity Recognition (NER)",
        "definition": "The subtask of information extraction that identifies and classifies key entities (Persons, Organizations, Locations, Dates) in text.",
        "why_useful": "Automates knowledge graph construction, relation extraction, and legal document indexing.",
        "python_example": "import nltk\nsent = nltk.pos_tag(nltk.word_tokenize('Google is in California.'))\nprint(nltk.ne_chunk(sent))",
        "expected_output": "(S (GPE Google/NNP) is/VBZ in/IN (GPE California/NNP) ./. )",
        "common_mistakes": "Expecting standard English rule-based NER taggers to recognize regional non-English names without fine-tuning."
    }
]

SAMPLE_LIBRARY = {
    "education": "Universities and research institutions collaborate on natural language processing curricula. Academic benchmarks evaluate multilingual comprehension and student assessment pipelines.",
    "technology": "Autonomous neural networks process textual instructions to generate optimized database schemas. Microservices architecture enables low-latency distributed computing across cloud clusters.",
    "sports": "The national football team executed strategic counter-attacks to secure a thrilling victory in the cup final. Midfielders controlled possession throughout ninety competitive minutes.",
    "business": "Global financial markets observed quarterly corporate earnings trends. Venture capital investments prioritized generative computing software and automated supply chain logistics.",
    "telugu": "సహజ భాషా ప్రాసెసింగ్ (NLP) కంప్యూటర్లకు మానవ భాషను అర్థం చేసుకునే మరియు విశ్లేషించే సామర్థ్యాన్ని అందిస్తుంది. ఇది అధునాతన సాంకేతికత.",
    "hindi": "प्राकृतिक भाषा प्रसंस्करण (NLP) कंप्यूटर को मानव भाषा को समझने, विश्लेषण करने और संसाधित करने में सक्षम बनाता है।"
}

@learning_bp.route("/topics", methods=["GET"])
def list_topics():
    return api_success({"topics": TOPICS, "total": len(TOPICS)})

@learning_bp.route("/topics/<topic_id>", methods=["GET"])
def get_topic(topic_id: str):
    for t in TOPICS:
        if t["id"] == topic_id:
            return api_success({"topic": t})
    raise APIException("TOPIC_NOT_FOUND", f"Learning topic '{topic_id}' not found.", status_code=404)

@learning_bp.route("/samples", methods=["GET"])
def list_samples():
    return api_success({"samples": SAMPLE_LIBRARY})
