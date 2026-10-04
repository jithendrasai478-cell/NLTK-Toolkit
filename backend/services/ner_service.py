from collections import Counter
from typing import Any, Dict, List
import nltk

def extract_entities(text: str) -> Dict[str, Any]:
    """
    Extract named entities using:
    1. Hugging Face BERT-base-NER (CoNLL-2003 trained transformer) if available
    2. NLTK Maximum Entropy Named Entity Chunker (fallback)
    """
    # 1. Try Hugging Face Transformer NER first
    try:
        from backend.providers.huggingface_provider import hf_extract_ner
        hf_res = hf_extract_ner(text)
        if hf_res and hf_res.get("entities"):
            return hf_res
    except Exception:
        pass

    # 2. Local NLTK Chunker
    sentences = nltk.sent_tokenize(text)
    entities: List[Dict[str, Any]] = []
    type_counts = Counter()

    for sent_idx, sent in enumerate(sentences, start=1):
        tokens = nltk.word_tokenize(sent)
        tagged = nltk.pos_tag(tokens)
        chunked = nltk.ne_chunk(tagged, binary=False)

        for subtree in chunked:
            if isinstance(subtree, nltk.Tree):
                entity_label = subtree.label()
                entity_tokens = [token for token, pos in subtree.leaves()]
                entity_text = " ".join(entity_tokens)
                
                # Friendly label mapping
                label_map = {
                    "GPE": "Location / Geo-Political Entity",
                    "PERSON": "Person",
                    "ORGANIZATION": "Organization",
                    "FACILITY": "Facility / Architecture",
                    "GSP": "Geo-Socio-Political Group"
                }
                friendly_label = label_map.get(entity_label, entity_label)
                type_counts[friendly_label] += 1

                entities.append({
                    "text": entity_text,
                    "label": entity_label,
                    "category": friendly_label,
                    "sentence_index": sent_idx
                })

    return {
        "total_entities_found": len(entities),
        "entities": entities,
        "category_breakdown": [{"category": cat, "count": cnt} for cat, cnt in type_counts.most_common()],
        "model": "NLTK Maximum Entropy Named Entity Chunker",
        "notice": "NLTK standard NER is trained on the ACE and Penn Treebank English corpora."
    }
