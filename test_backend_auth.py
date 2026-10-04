"""
Verification of backend Google auth handling for multiple distinct accounts,
persistence, JSON responses, and token management.
"""
import urllib.request
import json
import sqlite3

def run_backend_verification():
    print("=" * 60)
    print("RUNNING BACKEND GOOGLE AUTH MULTI-ACCOUNT VERIFICATION")
    print("=" * 60)

    from backend.app import create_app
    from backend.extensions import db
    from backend.models.user import User
    from google.oauth2 import id_token

    app = create_app('development')
    client = app.test_client()

    # Pre-existing user Jithendra Sai
    account_jithendra = {
        "iss": "https://accounts.google.com",
        "sub": "103743074659034551160",
        "email": "jithendrasai461@gmail.com",
        "name": "Jithendra Sai",
        "picture": "https://lh3.googleusercontent.com/a/jithendra"
    }

    # Second user: Account B
    account_b = {
        "iss": "https://accounts.google.com",
        "sub": "sub_google_account_b_888",
        "email": "nlp_researcher_b@gmail.com",
        "name": "Dr. Researcher B",
        "picture": "https://lh3.googleusercontent.com/a/researcher_b"
    }

    # Third user: Completely new Google account C
    account_c = {
        "iss": "https://accounts.google.com",
        "sub": "sub_google_account_c_999",
        "email": "brand_new_student@gmail.com",
        "name": "New NLP Student",
        "picture": "https://lh3.googleusercontent.com/a/student_c"
    }

    with app.app_context():
        # --- TEST 1: Google Account A (Jithendra Sai) ---
        print("\n[TEST 1] Logging in Google Account A (Jithendra Sai)...")
        id_token.verify_oauth2_token = lambda *args, **kwargs: account_jithendra
        res1 = client.post("/api/v1/auth/google", json={"credential": "mock_cred_jithendra"})
        assert res1.status_code == 200, f"Expected 200, got {res1.status_code}: {res1.get_json()}"
        data1 = res1.get_json()["data"]
        user1 = data1["user"]
        token1 = data1["access_token"]
        assert user1["email"] == "jithendrasai461@gmail.com"
        assert user1["google_id"] == "103743074659034551160"
        print(f" PASS: Account A authenticated successfully! ID: {user1['id']}, Username: {user1['username']}")

        # --- TEST 2: Verify /api/v1/auth/me with token A ---
        me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token1}"})
        assert me_res.status_code == 200
        assert me_res.get_json()["data"]["user"]["email"] == "jithendrasai461@gmail.com"
        print(" PASS: Profile verification with Token A succeeded!")

        # --- TEST 3: Google Account B (Second distinct Google account) ---
        print("\n[TEST 3] Logging in Google Account B (Dr. Researcher B)...")
        id_token.verify_oauth2_token = lambda *args, **kwargs: account_b
        res2 = client.post("/api/v1/auth/google", json={"credential": "mock_cred_b"})
        assert res2.status_code == 200, f"Expected 200, got {res2.status_code}: {res2.get_json()}"
        data2 = res2.get_json()["data"]
        user2 = data2["user"]
        token2 = data2["access_token"]
        assert user2["email"] == "nlp_researcher_b@gmail.com"
        assert user2["google_id"] == "sub_google_account_b_888"
        assert user2["id"] != user1["id"], "Account B must have a different user ID from Account A!"
        print(f" PASS: Account B created/authenticated independently! ID: {user2['id']}, Username: {user2['username']}")

        # --- TEST 4: Re-login Account A ---
        print("\n[TEST 4] Re-logging in with Account A...")
        id_token.verify_oauth2_token = lambda *args, **kwargs: account_jithendra
        res1_re = client.post("/api/v1/auth/google", json={"credential": "mock_cred_jithendra"})
        assert res1_re.status_code == 200
        assert res1_re.get_json()["data"]["user"]["id"] == user1["id"]
        print(" PASS: Account A re-authenticated successfully with existing record!")

        # --- TEST 5: Re-login Account B ---
        print("\n[TEST 5] Re-logging in with Account B...")
        id_token.verify_oauth2_token = lambda *args, **kwargs: account_b
        res2_re = client.post("/api/v1/auth/google", json={"credential": "mock_cred_b"})
        assert res2_re.status_code == 200
        assert res2_re.get_json()["data"]["user"]["id"] == user2["id"]
        print(" PASS: Account B re-authenticated successfully with existing record!")

        # --- TEST 6: Brand new Google Account C ---
        print("\n[TEST 6] Logging in with completely new Google Account C...")
        id_token.verify_oauth2_token = lambda *args, **kwargs: account_c
        res3 = client.post("/api/v1/auth/google", json={"credential": "mock_cred_c"})
        assert res3.status_code == 200
        user3 = res3.get_json()["data"]["user"]
        assert user3["email"] == "brand_new_student@gmail.com"
        assert user3["id"] != user1["id"] and user3["id"] != user2["id"]
        print(f" PASS: New Google user C registered and logged in! ID: {user3['id']}, Username: {user3['username']}")

        # --- TEST 7: Invalid Google Token returns structured JSON ---
        print("\n[TEST 7] Verifying structured JSON on token failure...")
        def raise_val_err(*args, **kwargs):
            raise ValueError("Token signature is invalid")
        id_token.verify_oauth2_token = raise_val_err
        err_res = client.post("/api/v1/auth/google", json={"credential": "invalid_jwt_token_here"})
        assert err_res.status_code == 401
        err_json = err_res.get_json()
        assert err_json["success"] is False
        assert "message" in err_json
        assert err_json["error"]["code"] == "INVALID_TOKEN"
        print(f" PASS: Returns structured JSON on error: {err_json}")

    print("\n" + "=" * 60)
    print("ALL BACKEND MULTI-ACCOUNT VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_backend_verification()
