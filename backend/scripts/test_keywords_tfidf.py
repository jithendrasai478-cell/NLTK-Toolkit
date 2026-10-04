from backend.services.keywords_service import extract_keywords
import json

text = "Machine learning algorithms analyze large text corpora to extract meaningful patterns and linguistic structures."
res = extract_keywords(text, top_n=6, method="tfidf")

print("=== KEYWORDS RESULTS (TOP 6) ===")
for k in res["keywords"]:
    print(f"#{k['rank']}  {k['keyword']:<24} [weight: {k['score']}] ({k['type']})")

print("\n=== DEBUG METRICS ===")
dbg = res["debug"]
print("Total features found:", dbg["total_features_found"])
print("Unigrams count:", dbg["unigrams_count"])
print("Bigrams count:", dbg["bigrams_count"])
print("Explanation:", dbg["explanation"])

print("\n=== RAW SCORES BEFORE TOP-6 FILTERING (ALL 23 FEATURES) ===")
for raw in dbg["raw_scores_before_filtering"]:
    print(f"#{raw['rank']:<2}  {raw['term']:<24} [weight: {raw['tfidf_score']}] ({raw['type']})")
