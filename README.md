# NLTK TOOLKIT — NLP FOR EVERYONE

A complete, production-ready, full-stack Natural Language Processing (NLP) web platform built with **Python**, **Flask**, **NLTK**, **scikit-learn**, **React 19**, and **Tailwind CSS**.

---

## Architecture Overview

```
d:\NLTK Kit\
├── backend/                       # Python Flask REST API & NLP pipeline
│   ├── app.py                     # Flask application factory
│   ├── config.py                  # Environment configuration (Dev, Test, Prod)
│   ├── extensions.py              # db, cors, limiter, jwt instances
│   ├── requirements.txt           # Python dependencies
│   ├── .env.example               # Environment variables template
│   ├── routes/                    # API route blueprints
│   │   ├── health_routes.py       # GET /api/v1/health
│   │   ├── nlp_routes.py          # All POST /api/v1/nlp/* endpoints
│   │   ├── auth_routes.py         # Registration, Login, Profile
│   │   ├── history_routes.py      # History & Favorites
│   │   └── learning_routes.py     # Educational topics & code samples
│   ├── services/                  # Core NLP service implementations
│   │   ├── summarizer_service.py  # Frequency-based & extractive summarization
│   │   ├── sentiment_service.py   # VADER compound/pos/neg/neu analysis
│   │   ├── keywords_service.py    # TF-IDF & frequency keyword extraction
│   │   ├── tokenizer_service.py   # Multilingual & Indian language tokenization
│   │   ├── classifier_service.py  # scikit-learn TF-IDF + Logistic Regression
│   │   ├── translator_service.py  # Pluggable translation provider abstraction
│   │   ├── rewriter_service.py    # Rule & model-assisted rewriting modes
│   │   ├── qa_service.py          # Extractive passage-question answering
│   │   ├── ner_service.py         # Named Entity Recognition
│   │   ├── statistics_service.py  # Text analytics & readability formulas
│   │   ├── linguistics_service.py # Stemming, Lemmatization, POS, N-grams, Stopwords
│   │   └── language_service.py    # Language detection & cosine similarity
│   ├── providers/                 # HuggingFace & external translation providers
│   ├── models/                    # SQLAlchemy models (User, History, Favorite)
│   └── tests/                     # 28 passing pytest test cases
│
├── frontend/                      # React 19 + Vite + Tailwind CSS frontend
│   ├── src/                       # React components, UI cards, modals & services
│   ├── public/                    # Static assets, logos & favicon
│   ├── index.html                 # Single page application HTML
│   ├── package.json               # Frontend dependencies & scripts
│   ├── vite.config.ts             # Vite server & backend API proxy configuration
│   ├── tailwind.config.js         # Tailwind styling & brand design tokens
│   ├── tsconfig.json              # TypeScript project reference configs
│   └── .env                       # Frontend environment configuration (Google Client ID)
│
└── package.json                   # Workspace root runner (npm run dev / build)
```

---

## Quickstart Guide for Windows & VS Code

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.13)
- **Node.js 18+** (Tested on Node.js v22)

### 2. Backend Setup
Open PowerShell in the project directory (`D:\NLTK Kit`):

```powershell
# 1. Activate virtual environment
.\backend\venv\Scripts\Activate.ps1

# 2. Install dependencies (if not already installed)
pip install -r backend/requirements.txt

# 3. Download verified NLTK corpora
python backend/scripts/download_nltk_data.py

# 4. Start the Flask backend server (runs on port 5001)
python -m backend.app
```

The Flask server is now live at `http://127.0.0.1:5001/`.

### 3. Frontend Setup
In a second PowerShell terminal in `D:\NLTK Kit`:

```powershell
# Option A: Run directly from the project root
npm run dev

# Option B: Navigate into the frontend folder
cd frontend
npm run dev
```

Open [`http://localhost:5173/`](http://localhost:5173/) in your web browser.

---

## Features & Supported Endpoints

| Feature | HTTP Endpoint | Description |
| :--- | :--- | :--- |
| **System Health** | `GET /api/v1/health` | Health status and verified NLTK resources |
| **Summarization** | `POST /api/v1/nlp/summarize` | Extractive sentence ranking with compression metrics |
| **Sentiment Analysis** | `POST /api/v1/nlp/sentiment` | VADER polarity scoring (Compound, Pos, Neg, Neu) |
| **Keyword Extraction** | `POST /api/v1/nlp/keywords` | TF-IDF & frequency ranking of key terms |
| **Tokenization** | `POST /api/v1/nlp/tokenize` | Sentence & word tokenization with Unicode support |
| **Text Classification** | `POST /api/v1/nlp/classify` | scikit-learn TF-IDF model (Tech, Business, Sports, etc.) |
| **Translation** | `POST /api/v1/nlp/translate` | Supports Telugu (`te`), Hindi (`hi`), Tamil (`ta`), French, Spanish, etc. |
| **Supported Languages**| `GET /api/v1/languages` | List of supported language codes |
| **Text Rewriting** | `POST /api/v1/nlp/rewrite` | Modes: Simplify, Formal, Informal, Shorten, Expand |
| **Question Answering** | `POST /api/v1/nlp/qa` | Extractive candidate retrieval from reference passage |
| **Named Entity (NER)** | `POST /api/v1/nlp/ner` | Persons, Organizations, Locations (GPE) |
| **Text Statistics** | `POST /api/v1/nlp/statistics` | Character count, word count, reading time |
| **Readability** | `POST /api/v1/nlp/readability` | Flesch Reading Ease & Grade Level metrics |
| **Stopword Removal** | `POST /api/v1/nlp/stopwords` | Filtered tokens with customizable preservation |
| **Stemming** | `POST /api/v1/nlp/stem` | Porter and Snowball stemmers |
| **Lemmatization** | `POST /api/v1/nlp/lemmatize` | WordNet dictionary base form lemmas |
| **POS Tagging** | `POST /api/v1/nlp/pos-tag` | Penn Treebank syntactic markers with definitions |
| **N-Grams** | `POST /api/v1/nlp/ngrams` | Unigrams, bigrams, trigrams, and frequency analysis |
| **Word Frequency** | `POST /api/v1/nlp/word-frequency` | Chart-ready top-k frequencies |
| **Language Detection** | `POST /api/v1/nlp/language-detection` | Unicode script & stopword profiling (Telugu, Hindi, English, etc.) |
| **Text Similarity** | `POST /api/v1/nlp/similarity` | TF-IDF vector space cosine similarity score |
| **Learning Center** | `GET /api/v1/learning/topics` | 16 comprehensive educational NLP guides |
| **Authentication** | `POST /api/v1/auth/register` | User account creation with JWT access tokens |
| **History Audit** | `GET /api/v1/history` | User activity audit log |

---

## Running Automated Tests

Run the full pytest suite from the project root:

```powershell
.\backend\venv\Scripts\python -m pytest -v
```

All 28 unit and integration tests verify endpoints, validation rules, multilingual processing, and database operations.
