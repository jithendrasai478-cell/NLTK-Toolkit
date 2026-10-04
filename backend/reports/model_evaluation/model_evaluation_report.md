# NLTK Toolkit - Model Training & Evaluation Report

Generated: 2026-09-20 14:35:03

## 1. Topic Classification (20 Newsgroups Dataset)
- **Model**: TF-IDF (1-2 ngrams, 15,000 features) + Logistic Regression (C=2.0)
- **Training Samples**: 12521 articles
- **Test Samples**: 2600 articles
- **Accuracy**: **87.65%**
- **Macro-F1 Score**: **0.8549**
- **Classes Supported**: `Technology`, `Science & Health`, `Sports`, `Politics`, `Business`, `Entertainment`

## 2. Sentiment Analysis (Stanford Sentiment Treebank SST-2)
- **Model**: TF-IDF (1-2 ngrams, 10,000 features) + Logistic Regression (C=1.5)
- **Training Samples**: 4999 sentences
- **Test Samples**: 1038 sentences
- **Accuracy**: **75.92%**
- **Macro-F1 Score**: **0.7579**

## 3. Multilingual Language Identification
- **Model**: Character N-gram TF-IDF (2-4 char ngrams) + Multinomial Naive Bayes
- **Training Samples**: 268 texts
- **Test Samples**: 67 texts
- **Accuracy**: **100.00%**
- **Languages Supported**: Telugu (`te`), Hindi (`hi`), Tamil (`ta`), Kannada (`kn`), English (`en`), French (`fr`), Spanish (`es`), German (`de`), Japanese (`ja`), Chinese (`zh`)
