"""
NLTK Toolkit - Hugging Face Datasets Acquisition Suite
======================================================
Fetches genuine Hugging Face Transformer datasets:
1. EdinburghNLP/xsum: Abstractive Summarization Benchmark (Articles & Reference Summaries)
2. Helsinki-NLP/opus-100 (en-te): English ↔ Telugu Parallel Translation Corpus
3. rajpurkar/squad_v2: Reading Comprehension & Extractive QA with Unanswerable Questions

Uses the user's authenticated Hugging Face API key to query datasets-server.huggingface.co.
"""

import os
import sys
import json
import time
from pathlib import Path
import requests
from dotenv import load_dotenv

# Reconfigure stdout for Windows console UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

RAW_DIR = BASE_DIR / "data" / "raw"
MANIFESTS_DIR = BASE_DIR / "data" / "manifests"

token = os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN")
headers = {"Authorization": f"Bearer {token}"} if token else {}

def fetch_hf_dataset_rows(dataset_name: str, config: str, split: str, limit: int = 100) -> list:
    """Fetch rows from Hugging Face datasets-server."""
    url = f"https://datasets-server.huggingface.co/rows?dataset={dataset_name}&config={config}&split={split}&offset=0&limit={limit}"
    print(f"Fetching from Hugging Face: {dataset_name} ({config}/{split}, {limit} rows)...")
    try:
        res = requests.get(url, headers=headers, timeout=25)
        if res.status_code == 200:
            data = res.json()
            rows = [item["row"] for item in data.get("rows", [])]
            print(f"  -> Successfully fetched {len(rows)} rows from Hugging Face!")
            return rows
        else:
            print(f"  -> Datasets-server returned {res.status_code}: {res.text[:100]}")
            return []
    except Exception as e:
        print(f"  -> Network error fetching {dataset_name}: {e}")
        return []

def main():
    print("==========================================================")
    print(" NLTK Toolkit: Hugging Face Transformer Dataset Importer")
    print("==========================================================")

    # 1. Fetch Hugging Face Summarization Dataset (EdinburghNLP/xsum)
    sum_dir = RAW_DIR / "summarization"
    sum_dir.mkdir(parents=True, exist_ok=True)
    sum_file = sum_dir / "hf_xsum_summaries.jsonl"
    
    xsum_rows = fetch_hf_dataset_rows("EdinburghNLP/xsum", "default", "validation", limit=100)
    if xsum_rows:
        with open(sum_file, "w", encoding="utf-8") as f:
            for r in xsum_rows:
                # xsum row schema: {"document": "...", "summary": "...", "id": "..."}
                entry = {
                    "document": r.get("document", ""),
                    "summary": r.get("summary", ""),
                    "id": str(r.get("id", "")),
                    "source": "Hugging Face EdinburghNLP/xsum",
                    "task": "Abstractive Neural Summarization"
                }
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"Saved Hugging Face Summarization dataset to {sum_file.name} ({sum_file.stat().st_size / 1024:.2f} KB)")

    # 2. Fetch Hugging Face Translation Dataset (Helsinki-NLP/opus-100 en-te)
    trans_dir = RAW_DIR / "translation"
    trans_dir.mkdir(parents=True, exist_ok=True)
    trans_file = trans_dir / "hf_opus_english_telugu.jsonl"

    opus_rows = fetch_hf_dataset_rows("Helsinki-NLP/opus-100", "en-te", "train", limit=100)
    if opus_rows:
        with open(trans_file, "w", encoding="utf-8") as f:
            for r in opus_rows:
                # opus row schema: {"translation": {"en": "...", "te": "..."}}
                trans = r.get("translation", {})
                entry = {
                    "english": trans.get("en", ""),
                    "telugu": trans.get("te", ""),
                    "source": "Hugging Face Helsinki-NLP/opus-100",
                    "language_pair": "en-te",
                    "task": "Neural Machine Translation"
                }
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"Saved Hugging Face English-Telugu translation dataset to {trans_file.name} ({trans_file.stat().st_size / 1024:.2f} KB)")

    # 3. Fetch Hugging Face QA Dataset (rajpurkar/squad_v2)
    qa_dir = RAW_DIR / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    qa_file = qa_dir / "hf_squad_v2_samples.jsonl"

    squad_rows = fetch_hf_dataset_rows("rajpurkar/squad_v2", "squad_v2", "validation", limit=100)
    if squad_rows:
        with open(qa_file, "w", encoding="utf-8") as f:
            for r in squad_rows:
                entry = {
                    "id": str(r.get("id", "")),
                    "title": r.get("title", ""),
                    "context": r.get("context", ""),
                    "question": r.get("question", ""),
                    "answers": r.get("answers", {}),
                    "source": "Hugging Face rajpurkar/squad_v2",
                    "task": "Reading Comprehension & QA"
                }
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"Saved Hugging Face SQuAD v2 dataset to {qa_file.name} ({qa_file.stat().st_size / 1024:.2f} KB)")

    # 4. Refresh Manifest
    manifest_path = MANIFESTS_DIR / "datasets.json"
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        # Check and add new HF entries
        hf_entries = [
            {
                "name": "Hugging Face XSum Summarization Benchmark",
                "task": "Abstractive Neural Summarization (BART)",
                "path": str(sum_file),
                "size_mb": round(sum_file.stat().st_size / (1024*1024), 3) if sum_file.exists() else 0,
                "license": "MIT / Academic",
                "source": "Hugging Face (EdinburghNLP/xsum)"
            },
            {
                "name": "Hugging Face OPUS-100 English-Telugu Parallel Corpus",
                "task": "Neural Machine Translation (NLLB-200)",
                "path": str(trans_file),
                "size_mb": round(trans_file.stat().st_size / (1024*1024), 3) if trans_file.exists() else 0,
                "license": "CC BY-SA 4.0",
                "source": "Hugging Face (Helsinki-NLP/opus-100)"
            },
            {
                "name": "Hugging Face SQuAD v2.0 Reading Comprehension",
                "task": "Context-Grounded Question Answering (RoBERTa)",
                "path": str(qa_file),
                "size_mb": round(qa_file.stat().st_size / (1024*1024), 3) if qa_file.exists() else 0,
                "license": "CC BY-SA 4.0",
                "source": "Hugging Face (rajpurkar/squad_v2)"
            }
        ]

        existing_names = {d["name"] for d in manifest.get("datasets", [])}
        for entry in hf_entries:
            if entry["name"] not in existing_names:
                manifest["datasets"].append(entry)

        # Recompute total bytes
        total_bytes = 0
        for root, _, files in os.walk(BASE_DIR / "data"):
            for fn in files:
                total_bytes += (Path(root) / fn).stat().st_size

        manifest["total_datasets"] = len(manifest["datasets"])
        manifest["total_size_bytes"] = total_bytes
        manifest["total_size_mb"] = round(total_bytes / (1024*1024), 2)
        manifest["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        print(f"\nManifest refreshed! Total datasets: {manifest['total_datasets']} | Total size: {manifest['total_size_mb']} MB")

if __name__ == "__main__":
    main()
