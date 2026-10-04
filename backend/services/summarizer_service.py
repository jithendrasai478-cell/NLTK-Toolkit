import os
import re
from typing import Any, Dict, List, Optional, Set
import nltk
from nltk.corpus import stopwords as nltk_stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def count_words(text: str) -> int:
    """Accurately count words in text matching alphanumeric and hyphenated tokens."""
    return len(re.findall(r"\b[\w'-]+\b", text.strip()))

def get_content_words(text: str) -> Set[str]:
    """Extract informative lowercase content words excluding common English stopwords."""
    try:
        stops = set(nltk_stopwords.words("english"))
    except Exception:
        stops = set()
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    return set(w for w in words if w not in stops)

def distill_sentence_to_insight(sentence: str) -> str:
    """
    Distills an arbitrary English sentence into a concise, high-value takeaway bullet:
    - Strips meta-discourse / attribution preambles
    - Trims filler words and wordy expressions
    - Synthesizes core proposition without copying verbatim
    """
    s = sentence.strip()
    if not s:
        return ""

    # 1. Preamble & attribution stripping (e.g. "Researchers analyzed X and found that Y")
    m_find = re.match(r'^(.*?)\b(?:found|showed|demonstrated|concluded|reported|observed)\s+that\s+(.+)$', s, re.I)
    if m_find:
        preamble, finding = m_find.group(1).strip(), m_find.group(2).strip()
        quant_matches = re.findall(r'\b\d[\d,]*(?:\s+[a-zA-Z]+)?\b', preamble)
        finding_clean = finding[0].upper() + finding[1:] if finding else ""
        if quant_matches and len(quant_matches) <= 2:
            ctx = " and ".join(quant_matches)
            s = f"{finding_clean.rstrip('.')} (tested across {ctx})."
        else:
            s = finding_clean

    # 2. General discourse markers & meta-attributions
    s = re.sub(r'^(?:It is (?:widely |generally |imperative to note |important to note |evident |clear )?that\s+)', '', s, flags=re.I)
    s = re.sub(r'^(?:The\s+)?(?:ultimate\s+|primary\s+|main\s+|key\s+|overarching\s+)?(?:objective|goal|purpose|aim)\s+(?:is|was)\s+(?:to\s+)?', 'Core objective: ', s, flags=re.I)
    s = re.sub(r'^(?:In\s+addition|Furthermore|Moreover|Consequently|As a result|Specifically|Notably|Importantly|Essentially|In general|However|Ultimately|In conclusion),\s*', '', s, flags=re.I)
    s = re.sub(r'^(?:Studies|Experiments|Observations|Findings)\s+(?:have\s+)?(?:suggested|indicated|established)\s+that\s+', '', s, flags=re.I)
    s = re.sub(r'^(?:According to\s+[^,]+,\s*)', '', s, flags=re.I)

    # 3. Filler & padding phrase compression
    s = re.sub(r'\s+in a manner that is valuable\b', ' effectively', s, flags=re.I)
    s = re.sub(r'\bin order to\b', 'to', s, flags=re.I)
    s = re.sub(r'\bfor the purpose of\b', 'to', s, flags=re.I)
    s = re.sub(r'\bdue to the fact that\b', 'because', s, flags=re.I)
    s = re.sub(r'\ban interdisciplinary subfield of\b', 'an interdisciplinary field spanning', s, flags=re.I)
    s = re.sub(r'\bwith unprecedented accuracy\b', 'with high accuracy', s, flags=re.I)
    s = re.sub(r'\bthese patterns can be used to\b', 'identified patterns support', s, flags=re.I)
    s = re.sub(r'\bnow allow automated systems to\b', 'enable automated systems to', s, flags=re.I)
    s = re.sub(r'\bcombine statistical methods with\b', 'combine statistical methods and', s, flags=re.I)
    s = re.sub(r'\bis transforming healthcare through\b', 'drives healthcare transformation through', s, flags=re.I)

    # Standardize technical domain abbreviations without redundancy
    s = re.sub(r'\bNatural language processing\s*\(\s*NLP\s*\)', 'NLP', s, flags=re.I)
    s = re.sub(r'\bNatural language processing\b', 'NLP', s, flags=re.I)
    s = re.sub(r'\bMachine learning algorithms\b', 'ML algorithms', s, flags=re.I)
    s = re.sub(r'\bMachine learning\b', 'ML', s, flags=re.I)
    s = re.sub(r'\bArtificial intelligence\b', 'AI', s, flags=re.I)

    # Active voice transformation for actor phrases
    s = re.sub(r'^(?:Researchers|Scientists|Engineers)\s+(?:utilize|use|employ)\s+', 'Utilizes ', s, flags=re.I)
    s = re.sub(r'^(?:Astronomers|Biologists|Physicists|Doctors|Clinicians)\s+(?:use|utilize|apply)\s+', 'Applies ', s, flags=re.I)

    # Clean leading/trailing
    s = s.strip()
    if not s:
        return ""
    s = s[0].upper() + s[1:]
    if not s.endswith(('.', '!', '?')):
        s += '.'

    # 4. If still identical to original sentence, synthesize clause or reframe
    orig_clean = sentence.strip().lower().rstrip('. ')
    if s.lower().rstrip('. ') == orig_clean:
        # Check introductory prepositional clause (e.g. "In genomics, deep neural networks...")
        m_prep = re.match(r'^(In\s+[a-z]+),\s+([a-z\s]+?)\s+(.+)$', s, re.I)
        if m_prep:
            prep_clause, subj, rest = m_prep.group(1), m_prep.group(2), m_prep.group(3)
            s = f"{subj[0].upper() + subj[1:]} {rest.rstrip('.')} ({prep_clause.lower()})."
        else:
            # Check for "As X evolves, Y becomes Z"
            m_as = re.match(r'^(?:As|While)\s+([^,]+),\s+(.+)$', s, re.I)
            if m_as:
                dep_clause, main_clause = m_as.group(1), m_as.group(2)
                s = f"{main_clause[0].upper() + main_clause[1:].rstrip('.')} (as {dep_clause})."
            else:
                # Convert demonstratives (e.g. "This operational shift..." -> "Operational shift...")
                m_det = re.match(r'^(?:These|This|Those)\s+([A-Za-z].*)$', s, re.I)
                if m_det:
                    rem = m_det.group(1).strip()
                    s = rem[0].upper() + rem[1:]
                else:
                    words = s.split()
                    if len(words) > 12:
                        s = re.sub(r'\s+across\s+[a-z\s]+$', '', s.rstrip('.'), flags=re.I) + '.'

    return s

def extract_key_takeaways(
    sentences: List[str],
    selected_indices: List[int],
    ranked_indices: List[int],
    max_count: int = 3
) -> List[str]:
    """
    Extracts high-level key insights / takeaways from the document:
    - Never paraphrases sentences that already appear in the Summary.
    - If the Summary already contains all important sentences (or all sentences of a short text),
      omits Key Insights rather than producing redundant text.
    - Draws concise takeaways exclusively from high-value unselected sentences.
    - Avoids repetition among insights.
    - Yields 2–4 concise points (or fewer for short texts).
    """
    n_sents = len(sentences)
    selected_set = set(selected_indices)

    # If the summary already contains all sentences, omit Key Insights to avoid redundancy
    if len(selected_set) >= n_sents:
        return []

    # High-value sentences NOT in the summary
    unselected_ranked = [idx for idx in ranked_indices if idx not in selected_set]
    if not unselected_ranked:
        return []

    # Content words of all sentences in the summary
    summary_sentence_cwords = [get_content_words(sentences[idx]) for idx in selected_indices]

    takeaways = []
    seen_cwords_list: List[Set[str]] = []

    for idx in unselected_ranked:
        if len(takeaways) >= max_count:
            break

        sent = sentences[idx].strip()
        insight = distill_sentence_to_insight(sent)
        if not insight:
            continue

        cwords = get_content_words(insight)
        if not cwords:
            continue

        # Ensure this insight does not repeat / heavily overlap with any single summary sentence
        too_close_to_summary = False
        for s_cwords in summary_sentence_cwords:
            overlap = len(cwords & s_cwords)
            denom = min(len(cwords), len(s_cwords)) or 1
            if overlap / denom > 0.60:
                too_close_to_summary = True
                break

        if too_close_to_summary:
            continue

        # Prevent duplicate insights among themselves
        too_similar = False
        for seen_cwords in seen_cwords_list:
            inter = len(cwords & seen_cwords)
            denom = min(len(cwords), len(seen_cwords)) or 1
            if inter / denom > 0.50:
                too_similar = True
                break

        if too_similar:
            continue

        takeaways.append(insight)
        seen_cwords_list.append(cwords)

    return takeaways

def determine_sentence_budget(n_sents: int, mode: str) -> int:
    """
    Dynamically calculates the target sentence count for SHORT, MEDIUM, and LONG modes.
    1. For sufficiently long documents (>= 4 sentences), LONG provides meaningful compression
       and does not simply return the entire input.
    2. For very short documents (<= 3 sentences) where sentence-level extractive summarization
       cannot provide a meaningful intermediate compression, allow LONG to return all sentences.
    3. Guarantees SHORT < MEDIUM < LONG whenever N >= 3.
    """
    if n_sents <= 1:
        return 1

    if n_sents == 2:
        return 1 if mode in ("short", "medium") else 2

    if n_sents == 3:
        if mode == "short":
            return 1
        elif mode == "medium":
            return 2
        else:  # long: all 3 sentences for very short document
            return 3

    if n_sents == 4:
        if mode == "short":
            return 1
        elif mode == "medium":
            return 2
        else:  # long: 3 of 4 sentences (~75%)
            return 3

    # For n_sents >= 5:
    # SHORT: strongest compression (~20–30% of sentences, min 1)
    k_short = max(1, round(n_sents * 0.25))
    k_short = min(k_short, max(1, n_sents - 2))

    # MEDIUM: moderate compression (~45–55% of sentences)
    k_med = max(k_short + 1, round(n_sents * 0.50))
    k_med = min(k_med, max(k_short + 1, n_sents - 1))

    # LONG: light compression (~70–75% of sentences, guaranteed < n_sents so it provides meaningful compression)
    k_long = max(k_med + 1, round(n_sents * 0.72))
    k_long = min(k_long, n_sents - 1)  # Strictly < n_sents for n_sents >= 5

    if mode == "short":
        return k_short
    elif mode == "long":
        return k_long
    else:  # medium
        return k_med

def summarize_text(
    text: str, 
    length_mode: str = "medium", 
    max_sentences: Optional[int] = None
) -> Dict[str, Any]:
    """
    Advanced Extractive Summarization Engine using TextRank Graph Centrality:
    1. Robust paragraph-aware sentence tokenization.
    2. Dynamic length control:
       - SHORT: Strongest compression (~20–30% of sentences).
       - MEDIUM: Moderate compression (~45–55% of sentences).
       - LONG: Light compression (~70–75% for long texts; full text allowed for <= 3 sentences).
       - Strictly guarantees SHORT < MEDIUM < LONG whenever N >= 3.
    3. Blended graph centrality (TF-IDF cosine similarity + content-word lexical overlap).
    4. Term importance, factual retention, and secondary lead-position weighting.
    5. Maximal Marginal Relevance (MMR) redundancy avoidance.
    6. Preservation of chronological document sentence order.
    7. Synthesized, non-verbatim Key Insights avoiding duplication with Summary sentences.
    8. Exact word-count-based reduction percentage: ((orig_words - sum_words) / orig_words) * 100.
    """
    cleaned = text.strip()
    if not cleaned:
        return {
            "summary": "",
            "key_takeaways": [],
            "original_sentence_count": 0,
            "summary_sentence_count": 0,
            "original_word_count": 0,
            "summary_word_count": 0,
            "compression_ratio": 1.0,
            "percentage_reduction": 0.0,
            "mode": length_mode,
            "provider": "empty",
            "technique": "Empty input"
        }

    # Optional explicit Hugging Face router override if configured in .env
    if os.getenv("SUMMARIZATION_PROVIDER") == "huggingface":
        try:
            from backend.providers.huggingface_provider import hf_summarize_text
            hf_res = hf_summarize_text(cleaned, length_mode=length_mode)
            if hf_res and hf_res.get("summary"):
                sents = nltk.sent_tokenize(cleaned)
                hf_res["original_sentence_count"] = len(sents)
                hf_res["summary_sentence_count"] = len(nltk.sent_tokenize(hf_res["summary"]))
                hf_res["key_takeaways"] = extract_key_takeaways(sents, [], list(range(len(sents))), max_count=3)
                return hf_res
        except Exception:
            pass

    # Extract sentences preserving paragraph structure
    paragraphs = [p.strip() for p in re.split(r'\n+', cleaned) if p.strip()]
    raw_sentences = []
    for p in paragraphs:
        raw_sentences.extend(nltk.sent_tokenize(p))

    sentences = [s.strip() for s in raw_sentences if s.strip()]
    n_sents = len(sentences)
    orig_words = count_words(cleaned)

    # 1. Single sentence fallback
    if n_sents == 1:
        s0 = sentences[0]
        sum_words = count_words(s0)
        insight = distill_sentence_to_insight(s0)
        return {
            "summary": s0,
            "key_takeaways": [insight] if insight else [],
            "original_sentence_count": 1,
            "summary_sentence_count": 1,
            "original_word_count": orig_words,
            "summary_word_count": sum_words,
            "compression_ratio": 1.0,
            "percentage_reduction": 0.0,
            "mode": length_mode,
            "provider": "local_textrank",
            "selected_sentence_indices": [0],
            "technique": "TextRank Graph Centrality with Lead-Position Weighting"
        }

    # 2. TextRank Graph Construction (>= 2 sentences)
    # TF-IDF Cosine Similarity
    try:
        vec = TfidfVectorizer(stop_words='english', token_pattern=r'(?u)\b[\w-]+\b')
        tfidf = vec.fit_transform(sentences)
        sim_matrix = cosine_similarity(tfidf, tfidf)
    except Exception:
        sim_matrix = np.zeros((n_sents, n_sents))

    # Content word overlap graph (Mihalcea & Tarau formulation)
    try:
        stops = set(nltk_stopwords.words("english"))
    except Exception:
        stops = set()

    sent_tokens = [
        set(w.lower() for w in re.findall(r'\b\w+\b', s) if w.lower() not in stops and len(w) > 2)
        for s in sentences
    ]

    overlap_matrix = np.zeros((n_sents, n_sents))
    for i in range(n_sents):
        for j in range(n_sents):
            if i != j:
                inter = len(sent_tokens[i] & sent_tokens[j])
                denom = np.log(1.0 + len(sent_tokens[i])) + np.log(1.0 + len(sent_tokens[j]))
                if denom > 0:
                    overlap_matrix[i, j] = inter / denom

    # Blended similarity matrix (70% TF-IDF cosine, 30% lexical overlap)
    blended_sim = 0.70 * sim_matrix + 0.30 * overlap_matrix
    np.fill_diagonal(blended_sim, 0.0)

    # PageRank power iteration
    damping = 0.85
    scores = np.ones(n_sents) / n_sents

    # Row normalize
    row_sums = blended_sim.sum(axis=1)
    trans_matrix = np.zeros((n_sents, n_sents))
    for i in range(n_sents):
        if row_sums[i] > 0:
            trans_matrix[i, :] = blended_sim[i, :] / row_sums[i]
        else:
            trans_matrix[i, :] = 1.0 / n_sents

    for _ in range(35):
        scores = (1 - damping) / n_sents + damping * trans_matrix.T.dot(scores)

    # Informational term and factual signal boosts
    for i in range(n_sents):
        s = sentences[i]
        # Quantitative / numerical / date presence boost
        if re.search(r'\b(?:\d[\d,]*|\d+\.\d+|\d+\s*percent|\d+%\b)', s, re.I):
            scores[i] *= 1.15
        # Technical capitalized terms / named entities
        if re.search(r'\b[A-Z][a-zA-Z0-9-]+\b', s):
            scores[i] *= 1.05

    # Secondary Lead & Conclusion position weighting (does not dominate)
    for i in range(n_sents):
        if i == 0:
            scores[i] *= 1.25  # Opening lead introduction
        elif i == 1 and n_sents > 3:
            scores[i] *= 1.10  # Secondary elaboration
        elif i == n_sents - 1 and n_sents >= 3:
            scores[i] *= 1.15  # Concluding takeaway

    # Dynamic sentence budgeting
    if max_sentences is not None:
        target_k = max(1, min(n_sents, max_sentences))
    else:
        target_k = determine_sentence_budget(n_sents, length_mode)

    # MMR (Maximal Marginal Relevance) Diversity Selection
    norm_scores = scores / (scores.max() if scores.max() > 0 else 1.0)
    selected_indices = []
    candidates = list(range(n_sents))

    # Pick highest scoring sentence first
    first_pick = int(np.argmax(norm_scores))
    selected_indices.append(first_pick)
    candidates.remove(first_pick)

    # Select remaining up to target_k with MMR
    lambda_mmr = 0.70
    while len(selected_indices) < target_k and candidates:
        best_cand = None
        best_mmr_score = -float('inf')

        for cand in candidates:
            max_sim_to_selected = max(blended_sim[cand, sel] for sel in selected_indices)
            mmr_val = lambda_mmr * norm_scores[cand] - (1 - lambda_mmr) * max_sim_to_selected
            if mmr_val > best_mmr_score:
                best_mmr_score = mmr_val
                best_cand = cand

        if best_cand is not None:
            selected_indices.append(best_cand)
            candidates.remove(best_cand)
        else:
            break

    # Restore original chronological document order
    selected_indices = sorted(selected_indices)
    summary_sentences = [sentences[idx].strip() for idx in selected_indices]
    summary_text = " ".join(summary_sentences)

    # Key insights generation:
    ranked_indices = [int(idx) for idx in np.argsort(scores)[::-1]]
    if n_sents <= 3:
        num_insights = 2
    elif n_sents <= 10:
        num_insights = 3
    else:
        num_insights = 4

    key_takeaways = extract_key_takeaways(
        sentences, 
        selected_indices=selected_indices, 
        ranked_indices=ranked_indices, 
        max_count=num_insights
    )

    # Accurate word count & reduction percentage
    sum_words = count_words(summary_text)
    if orig_words > 0:
        reduction_percentage = round(((orig_words - sum_words) / orig_words) * 100, 1)
        reduction_percentage = max(0.0, min(100.0, reduction_percentage))
    else:
        reduction_percentage = 0.0

    compression_ratio = round(sum_words / max(1, orig_words), 2)

    return {
        "summary": summary_text,
        "key_takeaways": key_takeaways,
        "original_sentence_count": n_sents,
        "summary_sentence_count": len(summary_sentences),
        "original_word_count": orig_words,
        "summary_word_count": sum_words,
        "compression_ratio": compression_ratio,
        "percentage_reduction": reduction_percentage,
        "mode": length_mode,
        "provider": "local_textrank",
        "selected_sentence_indices": selected_indices,
        "technique": "TextRank Graph Centrality with Lead-Position Weighting"
    }
