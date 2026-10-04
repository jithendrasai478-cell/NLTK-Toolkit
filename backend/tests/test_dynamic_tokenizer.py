import pytest
from backend.services.tokenizer_service import tokenize_text, parse_nlp_input, check_nltk_tokenizer_resources
from backend.utils.error_handlers import APIException
from backend.app import create_app

@pytest.fixture
def app():
    app = create_app('testing')
    return app

@pytest.fixture
def client(app):
    return app.test_client()

# =====================================================================
# TEST 1: Normal Word Tokenization
# =====================================================================
def test_normal_word_tokenization():
    raw = "Let's tokenize this sentence!"
    res = tokenize_text(raw)
    assert res["input_text"] == "Let's tokenize this sentence!"
    assert res["is_function_call"] is False
    assert res["function_name"] == "word_tokenize"
    assert res["processing_method"] == "NLTK word_tokenize"
    assert res["library_used"] == "NLTK"
    assert res["tokens"] == ["Let", "'s", "tokenize", "this", "sentence", "!"]
    assert res["token_count"] == 6
    assert res["sentence_count"] == 1
    assert res["character_count"] == len(raw)

# =====================================================================
# TEST 2: Function-Style word_tokenize Input
# =====================================================================
def test_function_style_word_tokenize():
    raw = 'word_tokenize("Let\'s tokenize this sentence!")'
    res = tokenize_text(raw)
    assert res["input_text"] == "Let's tokenize this sentence!"
    assert res["is_function_call"] is True
    assert res["function_name"] == "word_tokenize"
    assert res["processing_method"] == "NLTK word_tokenize"
    assert res["library_used"] == "NLTK"
    assert res["tokens"] == ["Let", "'s", "tokenize", "this", "sentence", "!"]
    assert res["token_count"] == 6
    assert res["sentence_count"] == 1
    assert res["character_count"] == len("Let's tokenize this sentence!")
    assert "word_tokenize" not in res["tokens"]

# =====================================================================
# TEST 3: Sentence Tokenization (sent_tokenize)
# =====================================================================
def test_sentence_tokenization():
    raw = 'sent_tokenize("First sentence. Second sentence! Third sentence?")'
    res = tokenize_text(raw)
    assert res["input_text"] == "First sentence. Second sentence! Third sentence?"
    assert res["is_function_call"] is True
    assert res["function_name"] == "sent_tokenize"
    assert res["processing_method"] == "NLTK sent_tokenize"
    assert res["library_used"] == "NLTK"
    assert res["sentences"] == ["First sentence.", "Second sentence!", "Third sentence?"]
    assert res["sentence_count"] == 3
    assert res["token_count"] == len(res["tokens"])

# =====================================================================
# TEST 4: Different Dynamic User Inputs
# =====================================================================
def test_dynamic_recalculation_across_different_inputs():
    inputs_and_expected = [
        ("Hello world.", 3, 1),
        ("Hello! How are you?", 6, 2),
        ("Natural Language Processing is interesting.", 6, 1),
        ("I love NLP.", 4, 1),
        ("One, two, three, four, five.", 10, 1),
    ]
    for text, exp_tokens, exp_sents in inputs_and_expected:
        res = tokenize_text(text)
        assert res["input_text"] == text
        assert res["token_count"] == exp_tokens, f"Failed on {text}: expected {exp_tokens}, got {res['token_count']}"
        assert res["sentence_count"] == exp_sents, f"Failed on {text}: expected {exp_sents}, got {res['sentence_count']}"
        assert res["character_count"] == len(text)
        assert len(res["tokens"]) == res["token_count"]

# =====================================================================
# TEST 5: Empty Input
# =====================================================================
def test_empty_input():
    with pytest.raises(APIException) as exc_info:
        tokenize_text("")
    assert exc_info.value.code == "EMPTY_INPUT"

    with pytest.raises(APIException) as exc_info2:
        tokenize_text("     ")
    assert exc_info2.value.code == "EMPTY_INPUT"

# =====================================================================
# TEST 6: Invalid Function Syntax
# =====================================================================
def test_invalid_function_syntax():
    with pytest.raises(APIException) as exc_info:
        tokenize_text('word_tokenize("unclosed string')
    assert exc_info.value.code == "INVALID_SYNTAX"

    with pytest.raises(APIException) as exc_info2:
        tokenize_text('word_tokenize(12345)')
    assert exc_info2.value.code == "INVALID_ARGUMENT"

    with pytest.raises(APIException) as exc_info3:
        tokenize_text('word_tokenize()')
    assert exc_info3.value.code == "INVALID_ARGUMENT"

# =====================================================================
# TEST 7: Unsupported Function (Security Rejection)
# =====================================================================
def test_unsupported_function_rejected():
    dangerous_inputs = [
        'os.system("rm -rf /")',
        'exec("print(1)")',
        'eval("1+1")',
        'custom_extractor("text")',
    ]
    for dangerous in dangerous_inputs:
        with pytest.raises(APIException) as exc_info:
            tokenize_text(dangerous)
        assert exc_info.value.code == "UNSUPPORTED_FUNCTION"
        assert exc_info.value.status_code == 400

# =====================================================================
# TEST 8: Missing NLTK Resources Detection
# =====================================================================
def test_missing_nltk_resources_handling(monkeypatch):
    import nltk
    def mock_find(prefix):
        raise LookupError("Resource not found")
    def mock_download(res, quiet=True):
        raise Exception("Offline network failure")
    
    monkeypatch.setattr(nltk.data, "find", mock_find)
    monkeypatch.setattr(nltk, "download", mock_download)

    with pytest.raises(APIException) as exc_info:
        check_nltk_tokenizer_resources()
    assert exc_info.value.code == "MISSING_NLTK_RESOURCE"
    assert exc_info.value.status_code == 500

# =====================================================================
# TEST 9: Backend / API Failure & Endpoint Integration
# =====================================================================
def test_api_tokenize_endpoint_success(client):
    res = client.post("/api/v1/nlp/tokenize", json={"text": 'word_tokenize("Let\'s tokenize this sentence!")'})
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["success"] is True
    data = json_data["data"]
    assert data["input_text"] == "Let's tokenize this sentence!"
    assert data["processing_method"] == "NLTK word_tokenize"
    assert data["library_used"] == "NLTK"
    assert data["token_count"] == 6
    assert data["tokens"] == ["Let", "'s", "tokenize", "this", "sentence", "!"]

def test_api_tokenize_endpoint_error_handling(client):
    # Test empty text
    res1 = client.post("/api/v1/nlp/tokenize", json={"text": ""})
    assert res1.status_code == 400
    assert res1.get_json()["success"] is False

    # Test unsupported function
    res2 = client.post("/api/v1/nlp/tokenize", json={"text": 'os.system("rm -rf /")'})
    assert res2.status_code == 400
    assert res2.get_json()["error"]["code"] == "UNSUPPORTED_FUNCTION"

    # Test invalid syntax
    res3 = client.post("/api/v1/nlp/tokenize", json={"text": 'word_tokenize(123)'})
    assert res3.status_code == 400
    assert res3.get_json()["error"]["code"] == "INVALID_ARGUMENT"
