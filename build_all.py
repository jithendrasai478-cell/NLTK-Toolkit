"""Automated Builder and Packager for NLTK Toolkit with Hybrid Search & Cross-Encoder.

Run this script:
    python build_all.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import zipfile

BASE_DIR = os.path.join(os.path.expanduser("~"), "nltk_toolkit_project")
PKG_DIR = os.path.join(BASE_DIR, "nltk_toolkit")
TESTS_DIR = os.path.join(BASE_DIR, "tests")

# ---------------------------------------------------------------------------
# File Content Declarations
# ---------------------------------------------------------------------------

FILES: dict[str, str] = {
    # 1. pyproject.toml
    os.path.join(BASE_DIR, "pyproject.toml"): """[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "nltk_toolkit"
version = "0.2.0"
description = "A modular NLP and Hybrid Search toolkit"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "nltk>=3.8.1",
    "numpy>=1.24.0",
    "sentence-transformers>=2.2.2",
    "torch>=2.0.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0.0"]

[tool.setuptools.packages.find]
where = ["."]
include = ["nltk_toolkit*"]
""",
    # 2. requirements.txt
    os.path.join(BASE_DIR, "requirements.txt"): """nltk>=3.8.1
numpy>=1.24.0
sentence-transformers>=2.2.2
torch>=2.0.0
pytest>=8.0.0
""",
    # 3. nltk_toolkit/resources.py
    os.path.join(PKG_DIR, "resources.py"): '''"""Resource management for NLTK datasets and models."""
from __future__ import annotations
import nltk

NLTK_RESOURCES = {
    "punkt": ("punkt", "tokenizers/punkt"),
    "punkt_tab": ("punkt_tab", "tokenizers/punkt_tab"),
    "stopwords": ("stopwords", "corpora/stopwords"),
    "wordnet": ("wordnet", "corpora/wordnet"),
    "omw-1.4": ("omw-1.4", "corpora/omw-1.4"),
    "averaged_perceptron_tagger": ("averaged_perceptron_tagger", "taggers/averaged_perceptron_tagger"),
    "averaged_perceptron_tagger_eng": ("averaged_perceptron_tagger_eng", "taggers/averaged_perceptron_tagger_eng"),
}

def is_resource_available(path: str) -> bool:
    try:
        nltk.data.find(path)
        return True
    except (LookupError, OSError):
        return False

def ensure_resource(key: str) -> bool:
    if key in NLTK_RESOURCES:
        name, path = NLTK_RESOURCES[key]
        if not is_resource_available(path):
            return bool(nltk.download(name, quiet=True))
    return True

def download_nltk_resources() -> dict[str, bool]:
    results = {}
    for key, (name, path) in NLTK_RESOURCES.items():
        if is_resource_available(path):
            results[key] = True
        else:
            results[key] = bool(nltk.download(name, quiet=True))
    return results
''',
    # 4. nltk_toolkit/tokenization.py
    os.path.join(PKG_DIR, "tokenization.py"): '''"""Tokenization utilities."""
from __future__ import annotations
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk_toolkit.resources import ensure_resource

def tokenize_sentences(text: str) -> list[str]:
    if not isinstance(text, str) or not text.strip():
        return []
    ensure_resource("punkt_tab")
    ensure_resource("punkt")
    return sent_tokenize(text)

def tokenize_words(text: str) -> list[str]:
    if not isinstance(text, str) or not text.strip():
        return []
    ensure_resource("punkt_tab")
    ensure_resource("punkt")
    return word_tokenize(text)
''',
    # 5. nltk_toolkit/preprocessing.py
    os.path.join(PKG_DIR, "preprocessing.py"): '''"""Text preprocessing and cleaning."""
from __future__ import annotations
import string
import unicodedata
from nltk.corpus import stopwords as nltk_stopwords
from nltk_toolkit.resources import ensure_resource
from nltk_toolkit.tokenization import tokenize_words

def normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFKC", text)

def remove_stopwords(tokens: list[str], language: str = "english") -> list[str]:
    ensure_resource("stopwords")
    stops = set(nltk_stopwords.words(language))
    return [t for t in tokens if t.lower() not in stops]

def preprocess_text(text: str, strip_stopwords: bool = True) -> str:
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")
    text = normalize_unicode(text.lower())
    text = text.translate(str.maketrans("", "", string.punctuation))
    tokens = tokenize_words(text)
    if strip_stopwords:
        tokens = remove_stopwords(tokens)
    return " ".join(tokens)
''',
    # 6. nltk_toolkit/embeddings.py
    os.path.join(PKG_DIR, "embeddings.py"): '''"""Dense sentence embeddings using SentenceTransformers."""
from __future__ import annotations
from typing import Any, Sequence
import numpy as np

_MODEL_CACHE: dict[str, Any] = {}
DEFAULT_MODEL = "all-MiniLM-L6-v2"

def get_embedding_model(model_name: str = DEFAULT_MODEL):
    if model_name not in _MODEL_CACHE:
        from sentence_transformers import SentenceTransformer
        _MODEL_CACHE[model_name] = SentenceTransformer(model_name)
    return _MODEL_CACHE[model_name]

def embed_texts(texts: Sequence[str] | str, model_name: str = DEFAULT_MODEL, normalize: bool = True) -> np.ndarray:
    if isinstance(texts, str):
        texts = [texts]
    if not texts:
        return np.empty((0, 0), dtype=np.float32)
    model = get_embedding_model(model_name)
    return model.encode(list(texts), normalize_embeddings=normalize, convert_to_numpy=True, show_progress_bar=False)

def semantic_similarity(text1: str, text2: str) -> float:
    vecs = embed_texts([text1, text2], normalize=True)
    return float(np.dot(vecs[0], vecs[1]))

def semantic_search(query: str, corpus: list[str], top_k: int = 3) -> list[dict]:
    if not corpus or top_k < 1:
        return []
    all_texts = [query] + corpus
    vecs = embed_texts(all_texts, normalize=True)
    q_vec = vecs[0]
    corpus_vecs = vecs[1:]
    scores = np.dot(corpus_vecs, q_vec)
    ranked = np.argsort(scores)[::-1][:top_k]
    return [{"corpus_id": int(i), "text": corpus[i], "score": round(float(scores[i]), 4)} for i in ranked]
''',
    # 7. nltk_toolkit/reranker.py
    os.path.join(PKG_DIR, "reranker.py"): '''"""Cross-Encoder Reranker for deep joint token comparison."""
from __future__ import annotations
from typing import Any

_RERANKER_CACHE: dict[str, Any] = {}
DEFAULT_RERANKER = "cross-encoder/ms-marco-MiniLM-L-6-v2"

def get_reranker_model(model_name: str = DEFAULT_RERANKER):
    if model_name not in _RERANKER_CACHE:
        from sentence_transformers import CrossEncoder
        _RERANKER_CACHE[model_name] = CrossEncoder(model_name)
    return _RERANKER_CACHE[model_name]

def rerank(query: str, candidate_docs: list[dict], model_name: str = DEFAULT_RERANKER, top_k: int | None = None) -> list[dict]:
    if not candidate_docs:
        return []
    model = get_reranker_model(model_name)
    pairs = [[query, doc["text"]] for doc in candidate_docs]
    scores = model.predict(pairs)
    
    reranked = []
    for doc, score in zip(candidate_docs, scores):
        updated = dict(doc)
        updated["rerank_score"] = round(float(score), 4)
        reranked.append(updated)
    
    reranked.sort(key=lambda d: d["rerank_score"], reverse=True)
    return reranked[:top_k] if top_k is not None else reranked
''',
    # 8. nltk_toolkit/hybrid_search.py
    os.path.join(PKG_DIR, "hybrid_search.py"): '''"""Hybrid Search combining BM25 Lexical and Dense Embeddings via RRF."""
from __future__ import annotations
import math
from collections import Counter
import numpy as np
from nltk_toolkit.embeddings import embed_texts
from nltk_toolkit.preprocessing import preprocess_text
from nltk_toolkit.tokenization import tokenize_words
from nltk_toolkit.reranker import rerank

class BM25Index:
    def __init__(self, corpus: list[str], k1: float = 1.5, b: float = 0.75):
        self.corpus = corpus
        self.k1 = k1
        self.b = b
        self.corpus_size = len(corpus)
        self.tokenized_corpus = []
        self.doc_lengths = []
        self.doc_freqs = Counter()
        self.idf = {}
        self._build_index()

    def _tokenize(self, text: str) -> list[str]:
        cleaned = preprocess_text(text, strip_stopwords=True)
        return [tok.lower() for tok in tokenize_words(cleaned) if tok.isalnum()]

    def _build_index(self):
        total_len = 0
        for doc in self.corpus:
            tokens = self._tokenize(doc)
            self.tokenized_corpus.append(tokens)
            l = len(tokens)
            self.doc_lengths.append(l)
            total_len += l
            for term in set(tokens):
                self.doc_freqs[term] += 1
        self.avg_doc_len = total_len / self.corpus_size if self.corpus_size else 0.0
        for term, freq in self.doc_freqs.items():
            self.idf[term] = math.log(1.0 + (self.corpus_size - freq + 0.5) / (freq + 0.5))

    def score(self, query: str) -> list[dict]:
        query_tokens = self._tokenize(query)
        scores = [0.0] * self.corpus_size
        for i, doc_tokens in enumerate(self.tokenized_corpus):
            doc_len = self.doc_lengths[i]
            if doc_len == 0:
                continue
            tf = Counter(doc_tokens)
            for q_term in query_tokens:
                if q_term not in tf:
                    continue
                num = tf[q_term] * (self.k1 + 1.0)
                den = tf[q_term] + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avg_doc_len))
                scores[i] += self.idf.get(q_term, 0.0) * (num / den)
        ranked = sorted(range(self.corpus_size), key=lambda idx: scores[idx], reverse=True)
        return [{"doc_id": idx, "text": self.corpus[idx], "score": round(scores[idx], 4)} for idx in ranked]

def hybrid_search(query: str, corpus: list[str], top_k: int = 3, rrf_k: int = 60, apply_rerank: bool = False) -> list[dict]:
    if not corpus or top_k < 1:
        return []
    bm25 = BM25Index(corpus)
    lex_res = bm25.score(query)
    lex_ranks = {item["doc_id"]: rank + 1 for rank, item in enumerate(lex_res)}

    all_texts = [query] + corpus
    vecs = embed_texts(all_texts, normalize=True)
    scores = np.dot(vecs[1:], vecs[0])
    sem_ranks = {int(idx): rank + 1 for rank, idx in enumerate(np.argsort(scores)[::-1])}

    rrf_scores = {}
    for doc_id in range(len(corpus)):
        r_lex = lex_ranks.get(doc_id, 999)
        r_sem = sem_ranks.get(doc_id, 999)
        rrf_scores[doc_id] = (1.0 / (rrf_k + r_lex)) + (1.0 / (rrf_k + r_sem))

    ranked_ids = sorted(rrf_scores.keys(), key=lambda d: rrf_scores[d], reverse=True)[:top_k]
    results = [
        {
            "doc_id": did,
            "text": corpus[did],
            "rrf_score": round(rrf_scores[did], 6),
            "lexical_rank": lex_ranks.get(did),
            "semantic_rank": sem_ranks.get(did),
        }
        for did in ranked_ids
    ]
    if apply_rerank:
        return rerank(query, results)
    return results
''',
    # 9. nltk_toolkit/__init__.py
    os.path.join(PKG_DIR, "__init__.py"): '''"""NLTK Toolkit Public Exports."""
from nltk_toolkit.resources import download_nltk_resources, ensure_resource
from nltk_toolkit.preprocessing import preprocess_text, remove_stopwords, normalize_unicode
from nltk_toolkit.tokenization import tokenize_words, tokenize_sentences
from nltk_toolkit.embeddings import embed_texts, semantic_search, semantic_similarity
from nltk_toolkit.reranker import rerank
from nltk_toolkit.hybrid_search import BM25Index, hybrid_search

__all__ = [
    "download_nltk_resources",
    "ensure_resource",
    "preprocess_text",
    "remove_stopwords",
    "normalize_unicode",
    "tokenize_words",
    "tokenize_sentences",
    "embed_texts",
    "semantic_search",
    "semantic_similarity",
    "rerank",
    "BM25Index",
    "hybrid_search",
]
''',
    # 10. tests/__init__.py
    os.path.join(TESTS_DIR, "__init__.py"): "",
    # 11. tests/test_hybrid_search.py
    os.path.join(TESTS_DIR, "test_hybrid_search.py"): '''from nltk_toolkit.hybrid_search import BM25Index, hybrid_search

def test_bm25_scoring():
    corpus = [
        "The quick brown fox jumps over the lazy dog",
        "Python data structures and algorithms",
    ]
    bm25 = BM25Index(corpus)
    res = bm25.score("quick dog")
    assert res[0]["doc_id"] == 0
    assert res[0]["score"] > 0.0

def test_hybrid_search_fusion():
    corpus = [
        "Docker container orchestration with Kubernetes",
        "A healthy diet consists of vegetables and fiber",
        "Setting up CI/CD pipelines using GitHub Actions and Docker",
    ]
    query = "How to automate deployments with containers?"
    results = hybrid_search(query, corpus, top_k=2, rrf_k=60)
    assert len(results) == 2
    returned_ids = {r["doc_id"] for r in results}
    assert 1 not in returned_ids
''',
    # 12. prototype_demo.py
    os.path.join(BASE_DIR, "prototype_demo.py"): '''from nltk_toolkit import download_nltk_resources
from nltk_toolkit.hybrid_search import hybrid_search

CORPUS = [
    "Error 404: The requested URL /auth/login was not found on this server.",
    "Regular aerobic workouts enhance cardiovascular health and decrease resting pulse rates.",
    "Engaging in physical jogging strengthens your heart muscles over time.",
    "Python 3.12 introduced improved interpreter performance and optimized tracebacks.",
    "To fix the 404 error in Python Flask routing, check your blueprint url prefix.",
]

def main():
    print("Pre-warming models and NLTK resources...")
    download_nltk_resources()

    query = "How to keep my heart healthy?"
    print(f"\\nQuery: {query}")
    print("=" * 60)

    results = hybrid_search(query, CORPUS, top_k=3, apply_rerank=True)
    for rank, res in enumerate(results, 1):
        print(f"#{rank} [RRF Score: {res['rrf_score']} | Cross-Encoder Rerank: {res.get('rerank_score')}]")
        print(f"    BM25 Rank: {res['lexical_rank']} | Semantic Rank: {res['semantic_rank']}")
        print(f"    Document: {res['text']}\\n")

if __name__ == "__main__":
    main()
''',
}


def build():
    print(f"--> Creating project layout at: {BASE_DIR}")
    os.makedirs(PKG_DIR, exist_ok=True)
    os.makedirs(TESTS_DIR, exist_ok=True)

    for path, content in FILES.items():
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  [+] Created {os.path.relpath(path, BASE_DIR)}")

    # Create downloadable zip
    zip_path = os.path.join(os.path.expanduser("~"), "nltk_toolkit_project.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(BASE_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, BASE_DIR)
                zipf.write(full_path, arcname=os.path.join("nltk_toolkit_project", rel_path))
    print(f"--> Standalone zip archive ready at: {zip_path}\n")

    # Run pytest directly from the created root
    print("--> Running pytest suite...")
    env = os.environ.copy()
    env["PYTHONPATH"] = BASE_DIR
    res = subprocess.run([sys.executable, "-m", "pytest", "tests/test_hybrid_search.py", "-v"], cwd=BASE_DIR, env=env)

    # Run prototype demo
    if res.returncode == 0:
        print("\n--> Running interactive prototype demo...")
        subprocess.run([sys.executable, "prototype_demo.py"], cwd=BASE_DIR, env=env)


if __name__ == "__main__":
    build()