import pytest
from backend.services.summarizer_service import summarize_text, count_words

def test_empty_and_whitespace():
    res = summarize_text("   ", length_mode="short")
    assert res["summary"] == ""
    assert res["original_sentence_count"] == 0
    assert res["percentage_reduction"] == 0.0

def test_single_sentence_fallback():
    text = "Artificial intelligence is transforming healthcare through rapid diagnostic analysis."
    res = summarize_text(text, length_mode="short")
    assert res["summary"] == text
    assert res["original_sentence_count"] == 1
    assert res["summary_sentence_count"] == 1
    assert res["percentage_reduction"] == 0.0
    assert len(res["key_takeaways"]) == 1
    assert res["key_takeaways"][0] != ""

def test_3_sentence_nlp_input():
    text = (
        "Natural language processing (NLP) is an interdisciplinary subfield of computer science and artificial intelligence. "
        "The ultimate objective is to read, decipher, understand, and make sense of human languages in a manner that is valuable. "
        "Modern neural models and transformers now allow automated systems to perform sentiment analysis, translation, and text summarization with unprecedented accuracy."
    )
    s_res = summarize_text(text, length_mode="short")
    m_res = summarize_text(text, length_mode="medium")
    l_res = summarize_text(text, length_mode="long")

    # Distinct sentence counts
    assert s_res["summary_sentence_count"] == 1
    assert m_res["summary_sentence_count"] == 2
    assert l_res["summary_sentence_count"] == 3

    # Distinct summaries
    assert s_res["summary"] != m_res["summary"]
    assert m_res["summary"] != l_res["summary"]

    # Accurate word count reductions
    assert s_res["original_word_count"] == 54
    assert s_res["summary_word_count"] == 14
    assert s_res["percentage_reduction"] == 74.1

    assert m_res["original_word_count"] == 54
    assert m_res["summary_word_count"] == 34
    assert m_res["percentage_reduction"] == 37.0

    # Rule 2: For 3-sentence document, LONG returns all sentences
    assert l_res["original_word_count"] == 54
    assert l_res["summary_word_count"] == 54
    assert l_res["percentage_reduction"] == 0.0

    # Key Insights are concise, non-verbatim, avoid echoing summary sentences, and omitted when all sentences are in summary
    assert len(s_res["key_takeaways"]) == 2
    assert len(m_res["key_takeaways"]) == 1
    assert len(l_res["key_takeaways"]) == 0  # Omitted because all 3 sentences are already in summary
    for k in m_res["key_takeaways"]:
        assert k not in [
            "Natural language processing (NLP) is an interdisciplinary subfield of computer science and artificial intelligence.",
            "The ultimate objective is to read, decipher, understand, and make sense of human languages in a manner that is valuable.",
            "Modern neural models and transformers now allow automated systems to perform sentiment analysis, translation, and text summarization with unprecedented accuracy."
        ]

def test_10_sentence_document():
    text = (
        "Artificial intelligence is rapidly transforming modern scientific discovery across multiple disciplines. "
        "Researchers utilize machine learning algorithms to analyze vast datasets far more quickly than traditional methods. "
        "In genomics, deep neural networks identify gene sequences associated with rare diseases. "
        "Astronomers use automated computer vision systems to detect exoplanets and classify distant galaxies. "
        "Furthermore, physics-informed neural networks solve complex differential equations in fluid dynamics and materials science. "
        "These computational models drastically reduce the time required to perform exploratory simulations. "
        "However, data quality, algorithmic bias, and interpretability remain significant engineering challenges. "
        "Rigorous validation protocols and domain-specific benchmarks are essential to ensure reliable real-world deployment. "
        "As foundational models evolve, interdisciplinary collaboration between domain scientists and machine learning engineers will become increasingly vital. "
        "Ultimately, integrating artificial intelligence into the scientific method promises to accelerate breakthroughs in medicine, energy, and environmental sustainability."
    )
    s_res = summarize_text(text, length_mode="short")
    m_res = summarize_text(text, length_mode="medium")
    l_res = summarize_text(text, length_mode="long")

    assert s_res["original_sentence_count"] == 10
    # Rule 9: SHORT < MEDIUM < LONG
    assert s_res["summary_sentence_count"] < m_res["summary_sentence_count"]
    assert m_res["summary_sentence_count"] < l_res["summary_sentence_count"]
    
    # Rule 1: LONG should still provide meaningful compression and not simply return entire input
    assert l_res["summary_sentence_count"] < 10
    assert l_res["percentage_reduction"] > 15.0

    # Word count hierarchy
    assert s_res["summary_word_count"] < m_res["summary_word_count"]
    assert m_res["summary_word_count"] < l_res["summary_word_count"]
    assert s_res["percentage_reduction"] > m_res["percentage_reduction"]
    assert m_res["percentage_reduction"] > l_res["percentage_reduction"]

def test_20_sentence_document():
    text = (
        "Modern cloud computing architectures rely heavily on distributed systems to provide scalable and fault-tolerant digital services. "
        "At the foundation of these platforms are clusters of commodity servers coordinated by distributed consensus protocols. "
        "Algorithms like Raft and Paxos ensure data consistency across multiple geographically replicated nodes. "
        "As microservice architectures became widespread, managing service-to-service communication introduced substantial operational complexity. "
        "Service meshes now provide dynamic traffic routing, load balancing, and mutual authentication across network boundaries. "
        "Containerization technologies such as Docker and orchestration engines like Kubernetes further streamlined continuous application deployment. "
        "Developers can package application code with its runtime dependencies, ensuring uniform behavior across environments. "
        "To manage persistent application state, distributed databases partition data across shards using consistent hashing. "
        "Replication strategies vary between strict linearizability and eventual consistency depending on specific latency trade-offs. "
        "The CAP theorem formally proves that a distributed system cannot simultaneously guarantee consistency, availability, and partition tolerance. "
        "Consequently, system architects must select acceptable trade-offs based on specific domain requirements. "
        "Serverless computing has recently emerged as an alternative execution model where cloud providers dynamically manage server allocation. "
        "In this paradigm, developers write discrete event-driven functions that execute on demand and scale automatically. "
        "This operational shift significantly reduces idle resource consumption and operational infrastructure overhead. "
        "However, cold start latencies and stateless execution constraints can present performance hurdles for latency-sensitive workloads. "
        "Edge computing complements centralized cloud infrastructure by processing data closer to end-user devices. "
        "Processing data locally at edge nodes reduces network bandwidth consumption and round-trip communication delays. "
        "This architecture is especially critical for time-sensitive applications such as autonomous vehicles, robotics, and industrial automation. "
        "Observability tools including distributed tracing, structured logging, and real-time metrics collection have become indispensable for diagnosing transient failures. "
        "In conclusion, the continued evolution of distributed infrastructure balances scalability, reliability, and computational efficiency across complex computing environments."
    )
    s_res = summarize_text(text, length_mode="short")
    m_res = summarize_text(text, length_mode="medium")
    l_res = summarize_text(text, length_mode="long")

    assert s_res["original_sentence_count"] == 20
    # Rule 9: SHORT < MEDIUM < LONG
    assert s_res["summary_sentence_count"] < m_res["summary_sentence_count"]
    assert m_res["summary_sentence_count"] < l_res["summary_sentence_count"]

    # Rule 1: LONG provides meaningful compression (e.g. 14 of 20, < 20)
    assert l_res["summary_sentence_count"] < 20
    assert l_res["percentage_reduction"] >= 20.0

    # Rule 4: Reduction percentage accurately computed
    assert s_res["percentage_reduction"] > m_res["percentage_reduction"]
    assert m_res["percentage_reduction"] > l_res["percentage_reduction"]

def test_numerical_retention():
    text = "Researchers analyzed 10,000 documents over 25 days and found that the proposed method improved classification accuracy by 15 percent."
    res = summarize_text(text, length_mode="short")
    assert "10,000" in res["summary"]
    assert "25 days" in res["summary"]
    assert "15 percent" in res["summary"]
    assert len(res["key_takeaways"]) >= 1

def test_original_order_preserved():
    text = (
        "First sentence sets the foundational premise. "
        "Second sentence elaborates with specific technical details. "
        "Third sentence introduces an alternative perspective. "
        "Fourth sentence provides concrete experimental measurements. "
        "Fifth sentence concludes with final architectural takeaways."
    )
    res = summarize_text(text, length_mode="medium")
    indices = res["selected_sentence_indices"]
    assert indices == sorted(indices)

def test_api_endpoint(client):
    article = (
        "Natural language processing is an interdisciplinary subfield of linguistics, computer science, and AI. "
        "It focuses on the interactions between human language and computational algorithms. "
        "Modern NLP combines computational linguistics with deep learning models. "
        "These technologies enable computers to process human language in the form of text or voice data. "
        "Its applications include sentiment analysis, machine translation, and speech recognition."
    )
    for mode in ["short", "medium", "long"]:
        res = client.post("/api/v1/nlp/summarize", json={"text": article, "options": {"summary_length": mode}})
        assert res.status_code == 200
        data = res.get_json()["data"]
        assert "summary" in data
        assert "key_takeaways" in data
        assert "percentage_reduction" in data
        assert data["technique"] == "TextRank Graph Centrality with Lead-Position Weighting"
