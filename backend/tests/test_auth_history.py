def test_register_and_login(client):
    # Registration
    reg_res = client.post("/api/v1/auth/register", json={
        "username": "nlpdeveloper",
        "email": "nlp@example.com",
        "password": "secretpassword123"
    })
    assert reg_res.status_code == 201
    reg_data = reg_res.get_json()["data"]
    assert "access_token" in reg_data
    assert reg_data["user"]["username"] == "nlpdeveloper"

    # Login
    login_res = client.post("/api/v1/auth/login", json={
        "email": "nlp@example.com",
        "password": "secretpassword123"
    })
    assert login_res.status_code == 200
    token = login_res.get_json()["data"]["access_token"]

    # Profile
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.get_json()["data"]["user"]["email"] == "nlp@example.com"

def test_history_crud(client):
    # Add history
    add_res = client.post("/api/v1/history", json={
        "tool_name": "sentiment",
        "input_snippet": "This is a great tool!",
        "output_summary": "Positive (0.95)",
        "processing_time_ms": 14.2
    })
    assert add_res.status_code == 201
    item_id = add_res.get_json()["data"]["history_item"]["id"]

    # List history
    list_res = client.get("/api/v1/history")
    assert list_res.status_code == 200
    assert list_res.get_json()["data"]["count"] >= 1

    # Delete history
    del_res = client.delete(f"/api/v1/history/{item_id}")
    assert del_res.status_code == 200

def test_learning_routes(client):
    res = client.get("/api/v1/learning/topics")
    assert res.status_code == 200
    topics = res.get_json()["data"]["topics"]
    assert len(topics) >= 5

    samples_res = client.get("/api/v1/learning/samples")
    assert samples_res.status_code == 200
    assert "telugu" in samples_res.get_json()["data"]["samples"]

def test_google_auth_missing_credential(client):
    res = client.post("/api/v1/auth/google", json={})
    assert res.status_code == 400
    assert res.get_json()["error"]["code"] == "MISSING_CREDENTIAL"

def test_google_auth_unconfigured(client, monkeypatch):
    monkeypatch.setitem(client.application.config, "GOOGLE_CLIENT_ID", "")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "")
    res = client.post("/api/v1/auth/google", json={"credential": "sample_token"})
    assert res.status_code == 500
    assert res.get_json()["error"]["code"] == "GOOGLE_CONFIG_ERROR"

def test_google_auth_invalid_token(client, monkeypatch):
    from google.oauth2 import id_token
    monkeypatch.setitem(client.application.config, "GOOGLE_CLIENT_ID", "mock-google-client-id.apps.googleusercontent.com")
    
    def mock_verify_invalid(*args, **kwargs):
        raise ValueError("Token is expired or invalid")
        
    monkeypatch.setattr(id_token, "verify_oauth2_token", mock_verify_invalid)
    
    res = client.post("/api/v1/auth/google", json={"credential": "invalid_jwt_token"})
    assert res.status_code == 401
    assert res.get_json()["error"]["code"] == "INVALID_TOKEN"

def test_google_auth_success_new_user(client, monkeypatch):
    from google.oauth2 import id_token
    monkeypatch.setitem(client.application.config, "GOOGLE_CLIENT_ID", "mock-google-client-id.apps.googleusercontent.com")
    
    fake_payload = {
        "iss": "https://accounts.google.com",
        "sub": "google-user-1234567890",
        "email": "testgoogleuser@gmail.com",
        "email_verified": True,
        "name": "Google Test User",
        "picture": "https://lh3.googleusercontent.com/a/fake_photo"
    }
    monkeypatch.setattr(id_token, "verify_oauth2_token", lambda *args, **kwargs: fake_payload)
    
    res = client.post("/api/v1/auth/google", json={"credential": "valid_mock_credential"})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "access_token" in data
    assert data["user"]["email"] == "testgoogleuser@gmail.com"
    assert data["user"]["google_id"] == "google-user-1234567890"
    assert data["user"]["display_name"] == "Google Test User"
    assert data["user"]["avatar_url"] == "https://lh3.googleusercontent.com/a/fake_photo"
    
    # Repeat login with existing user
    res2 = client.post("/api/v1/auth/google", json={"credential": "valid_mock_credential"})
    assert res2.status_code == 200
    data2 = res2.get_json()["data"]
    assert data2["user"]["id"] == data["user"]["id"]

def test_google_auth_multiple_distinct_accounts(client, monkeypatch):
    from google.oauth2 import id_token
    monkeypatch.setitem(client.application.config, "GOOGLE_CLIENT_ID", "mock-google-client-id.apps.googleusercontent.com")

    # Account A
    account_a_payload = {
        "iss": "https://accounts.google.com",
        "sub": "sub_account_a_99901",
        "email": "user_a@gmail.com",
        "name": "Alice Wonderland",
        "picture": "https://lh3.googleusercontent.com/alice.jpg"
    }
    monkeypatch.setattr(id_token, "verify_oauth2_token", lambda *args, **kwargs: account_a_payload)
    res_a = client.post("/api/v1/auth/google", json={"credential": "mock_cred_a"})
    assert res_a.status_code == 200
    user_a = res_a.get_json()["data"]["user"]
    assert user_a["email"] == "user_a@gmail.com"
    assert user_a["google_id"] == "sub_account_a_99901"

    # Account B (completely different account)
    account_b_payload = {
        "iss": "https://accounts.google.com",
        "sub": "sub_account_b_99902",
        "email": "user_b@gmail.com",
        "name": "Bob Builder",
        "picture": "https://lh3.googleusercontent.com/bob.jpg"
    }
    monkeypatch.setattr(id_token, "verify_oauth2_token", lambda *args, **kwargs: account_b_payload)
    res_b = client.post("/api/v1/auth/google", json={"credential": "mock_cred_b"})
    assert res_b.status_code == 200
    user_b = res_b.get_json()["data"]["user"]
    assert user_b["email"] == "user_b@gmail.com"
    assert user_b["google_id"] == "sub_account_b_99902"
    assert user_b["id"] != user_a["id"]

    # Account C (no display name, dots in email)
    account_c_payload = {
        "iss": "https://accounts.google.com",
        "sub": "sub_account_c_99903",
        "email": "charlie.smith.research@gmail.com",
        "name": "",
        "picture": ""
    }
    monkeypatch.setattr(id_token, "verify_oauth2_token", lambda *args, **kwargs: account_c_payload)
    res_c = client.post("/api/v1/auth/google", json={"credential": "mock_cred_c"})
    assert res_c.status_code == 200
    user_c = res_c.get_json()["data"]["user"]
    assert user_c["email"] == "charlie.smith.research@gmail.com"
    assert user_c["id"] != user_a["id"]
    assert user_c["id"] != user_b["id"]

    # Re-login with Account A should return Account A
    monkeypatch.setattr(id_token, "verify_oauth2_token", lambda *args, **kwargs: account_a_payload)
    res_a2 = client.post("/api/v1/auth/google", json={"credential": "mock_cred_a"})
    assert res_a2.status_code == 200
    assert res_a2.get_json()["data"]["user"]["id"] == user_a["id"]

    # Re-login with Account B should return Account B
    monkeypatch.setattr(id_token, "verify_oauth2_token", lambda *args, **kwargs: account_b_payload)
    res_b2 = client.post("/api/v1/auth/google", json={"credential": "mock_cred_b"})
    assert res_b2.status_code == 200
    assert res_b2.get_json()["data"]["user"]["id"] == user_b["id"]

def test_google_auth_links_existing_email_account(client, monkeypatch):
    from google.oauth2 import id_token
    monkeypatch.setitem(client.application.config, "GOOGLE_CLIENT_ID", "mock-google-client-id.apps.googleusercontent.com")

    # First register user via standard email/password
    client.post("/api/v1/auth/register", json={
        "username": "pre_registered_user",
        "email": "preregistered@example.com",
        "password": "Password123!"
    })

    # Now login using Google with the same email
    google_payload = {
        "iss": "https://accounts.google.com",
        "sub": "sub_preregistered_google_id",
        "email": "preregistered@example.com",
        "name": "Pre Registered Linked",
        "picture": "https://lh3.googleusercontent.com/photo.png"
    }
    monkeypatch.setattr(id_token, "verify_oauth2_token", lambda *args, **kwargs: google_payload)
    res = client.post("/api/v1/auth/google", json={"credential": "mock_cred_link"})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["user"]["email"] == "preregistered@example.com"
    assert data["user"]["google_id"] == "sub_preregistered_google_id"

def test_json_error_structure_on_auth_failure(client):
    res = client.post("/api/v1/auth/login", json={"email": "nonexistent@user.com", "password": "wrong"})
    assert res.status_code == 401
    json_data = res.get_json()
    assert json_data["success"] is False
    assert "message" in json_data
    assert "error" in json_data
    assert json_data["error"]["code"] == "INVALID_CREDENTIALS"

