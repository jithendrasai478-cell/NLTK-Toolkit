import os
import re
import secrets
from flask import Blueprint, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from backend.extensions import db
from backend.models.user import User
from backend.utils.error_handlers import api_success, APIException
from backend.utils.validators import validate_json_body

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = validate_json_body()
    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email:
        raise APIException("MISSING_EMAIL", "Email address is required.", status_code=400)

    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise APIException("INVALID_EMAIL", "A valid email address is required.", status_code=400)

    if not username:
        username = email.split("@")[0]

    raw_username = re.sub(r'[^a-zA-Z0-9_]', '_', username)
    raw_username = re.sub(r'_+', '_', raw_username).strip('_')
    if len(raw_username) < 3:
        raw_username = f"{raw_username}user" if raw_username else "nltk_user"
    username = raw_username[:30]

    if len(password) < 6:
        raise APIException("WEAK_PASSWORD", "Password must be at least 6 characters long.", status_code=400)

    if User.query.filter_by(email=email).first():
        raise APIException("EMAIL_EXISTS", f"Email '{email}' is already registered.", status_code=409)

    base_username = username[:25]
    counter = 1
    while User.query.filter_by(username=username).first():
        username = f"{base_username[:20]}_{counter}"
        counter += 1

    try:
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Registration database error: %s", str(e))
        raise APIException("DATABASE_ERROR", "Failed to create user account. Please try again.", status_code=500)

    try:
        access_token = create_access_token(identity=str(user.id))
    except Exception as e:
        current_app.logger.exception("JWT generation error during register: %s", str(e))
        raise APIException("TOKEN_ERROR", "Account created, but failed to generate session token.", status_code=500)

    return api_success({
        "user": user.to_dict(),
        "access_token": access_token
    }, status_code=201)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = validate_json_body()
    identifier = data.get("email", "").strip().lower() or data.get("username", "").strip()
    password = data.get("password", "")

    if not identifier or not password:
        raise APIException("MISSING_CREDENTIALS", "Email and password are required.", status_code=400)

    user = User.query.filter((User.email == identifier) | (User.username == identifier)).first()
    if not user or not user.check_password(password):
        raise APIException("INVALID_CREDENTIALS", "Invalid email or password.", status_code=401)

    try:
        access_token = create_access_token(identity=str(user.id))
    except Exception as e:
        current_app.logger.exception("JWT generation error during login: %s", str(e))
        raise APIException("TOKEN_ERROR", "Failed to generate session token.", status_code=500)

    return api_success({
        "user": user.to_dict(),
        "access_token": access_token
    })

@auth_bp.route("/google", methods=["POST"])
def google_auth():
    data = validate_json_body()
    credential = data.get("credential") or data.get("token") or data.get("id_token")
    if not credential:
        raise APIException("MISSING_CREDENTIAL", "Google credential token is required.", status_code=400)

    google_client_id = (current_app.config.get("GOOGLE_CLIENT_ID") or os.getenv("GOOGLE_CLIENT_ID", "")).strip()
    if not google_client_id or google_client_id == "YOUR_GOOGLE_CLIENT_ID":
        raise APIException(
            "GOOGLE_CONFIG_ERROR",
            "Google Client ID is not configured on the server. Please set GOOGLE_CLIENT_ID in backend/.env.",
            status_code=500
        )

    try:
        id_info = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            audience=google_client_id,
            clock_skew_in_seconds=10
        )
    except ValueError as e:
        err_msg = str(e)
        current_app.logger.warning("Google token verification ValueError: %s", err_msg)
        if "Wrong recipient" in err_msg or "audience" in err_msg.lower():
            raise APIException("INVALID_AUDIENCE", f"Google token audience mismatch: {err_msg}", status_code=401)
        raise APIException("INVALID_TOKEN", f"Invalid Google token: {err_msg}", status_code=401)
    except Exception as e:
        current_app.logger.exception("Google token verification unexpected error: %s", str(e))
        raise APIException("VERIFICATION_FAILED", f"Google token verification failed: {str(e)}", status_code=401)

    # Verify token issuer
    issuer = id_info.get("iss", "")
    if issuer not in ["accounts.google.com", "https://accounts.google.com"]:
        raise APIException("INVALID_ISSUER", "Google token has an invalid issuer.", status_code=401)

    # Extract verified profile details
    google_sub = str(id_info.get("sub", "")).strip()
    email = id_info.get("email", "").strip().lower()
    name = (id_info.get("name") or "").strip()
    picture = (id_info.get("picture") or "").strip()

    if not email:
        raise APIException("MISSING_EMAIL", "Google account did not provide an email address.", status_code=400)

    # Check if user already exists:
    # 1. Lookup by Google sub ID
    user = None
    if google_sub:
        user = User.query.filter_by(google_id=google_sub).first()

    # 2. Lookup by email if not found by Google sub
    if not user:
        user = User.query.filter_by(email=email).first()

    if not user:
        # Create brand-new user for this Google account
        raw_seed = name if name else email.split("@")[0]
        clean_seed = re.sub(r'[^a-zA-Z0-9_]', '_', raw_seed.lower().strip())
        clean_seed = re.sub(r'_+', '_', clean_seed).strip('_')
        if len(clean_seed) < 3:
            clean_seed = f"{clean_seed}user" if clean_seed else "google_user"
        base_username = clean_seed[:25]
        username = base_username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username[:20]}_{counter}"
            counter += 1

        user = User(
            username=username,
            display_name=name or username,
            email=email,
            google_id=google_sub or None,
            avatar_url=picture or None
        )
        user.set_password(secrets.token_urlsafe(32))
        try:
            db.session.add(user)
            db.session.commit()
            current_app.logger.info("Created new Google user: %s (ID: %s)", email, user.id)
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception("Database error while creating Google user: %s", str(e))
            raise APIException("DATABASE_ERROR", "Failed to create user account. Please try again.", status_code=500)
    else:
        # User exists: link Google ID, sync name and avatar if needed
        updated = False
        if google_sub and user.google_id != google_sub:
            # Check if another user already has this google_id
            existing_sub_user = User.query.filter_by(google_id=google_sub).first()
            if not existing_sub_user:
                user.google_id = google_sub
                updated = True
        if name and getattr(user, 'display_name', None) != name:
            user.display_name = name
            updated = True
        if picture and user.avatar_url != picture:
            user.avatar_url = picture
            updated = True

        if updated:
            try:
                db.session.commit()
                current_app.logger.info("Updated existing Google user profile: %s (ID: %s)", email, user.id)
            except Exception as e:
                db.session.rollback()
                current_app.logger.exception("Database error while updating Google user: %s", str(e))
                # Non-fatal: if profile update fails, still allow login with existing record

    try:
        access_token = create_access_token(identity=str(user.id))
    except Exception as e:
        current_app.logger.exception("JWT generation error during Google login: %s", str(e))
        raise APIException("TOKEN_ERROR", "Failed to generate authentication session.", status_code=500)

    return api_success({
        "user": user.to_dict(),
        "access_token": access_token
    })

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))
    if not user:
        raise APIException("USER_NOT_FOUND", "User profile not found.", status_code=404)

    return api_success({"user": user.to_dict()})
