"""
Dedicated NLTK Data Downloader Script
Downloads all required lexical resources and models required for the NLTK Toolkit.
Run this script once during backend setup.
"""
import sys
import nltk

# Ensure standard UTF-8 output on Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

RESOURCES = [
    'punkt',
    'punkt_tab',
    'stopwords',
    'wordnet',
    'omw-1.4',
    'vader_lexicon',
    'averaged_perceptron_tagger',
    'averaged_perceptron_tagger_eng',
    'maxent_ne_chunker',
    'maxent_ne_chunker_tab',
    'words',
]

def download_all():
    print("==========================================")
    print("NLTK Toolkit -- Resource Download Started")
    print("==========================================")
    failed = []
    for res in RESOURCES:
        print(f"Checking / downloading '{res}'...")
        try:
            nltk.download(res, quiet=True)
            print(f"  [OK] {res} downloaded/verified.")
        except Exception as e:
            print(f"  [FAIL] Failed to download {res}: {e}")
            failed.append(res)
            
    print("==========================================")
    if failed:
        print(f"Warning: {len(failed)} resource(s) could not be downloaded: {failed}")
    else:
        print("All required NLTK resources are installed and verified successfully!")
    print("==========================================")

if __name__ == '__main__':
    download_all()
