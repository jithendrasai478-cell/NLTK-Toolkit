import os
from pathlib import Path
from dotenv import load_dotenv

import sys
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR.parent) not in sys.path:
    sys.path.insert(0, str(BASE_DIR.parent))

# Ensure backend/.env is loaded before Config class evaluates
# Use override=True so that values in backend/.env take precedence
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)

# Also check project root .env as fallback if present
root_env_path = BASE_DIR.parent / ".env"
if root_env_path.exists():
    load_dotenv(root_env_path, override=False)

# Canonical SQLite database file inside backend/instance/
canonical_db_file = (BASE_DIR / "instance" / "nltk_toolkit.db").resolve()
canonical_db_file.parent.mkdir(parents=True, exist_ok=True)

raw_db_url = os.getenv("DATABASE_URL", "").strip()
if not raw_db_url or raw_db_url == "sqlite:///nltk_toolkit.db":
    DEFAULT_DB_URI = f"sqlite:///{canonical_db_file.as_posix()}"
else:
    DEFAULT_DB_URI = raw_db_url

class Config:
    PORT = int(os.getenv("PORT", 5001))
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = DEFAULT_DB_URI
    
    # CORS
    FRONTEND_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "FRONTEND_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174"
        ).split(",")
        if origin.strip()
    ]
    
    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "60")) * 60

    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()

    # Configurable Default User Credentials
    DEFAULT_USER_EMAIL = os.getenv("DEFAULT_USER_EMAIL", "demo@nltk.org")
    DEFAULT_USER_PASSWORD = os.getenv("DEFAULT_USER_PASSWORD", "DemoPassword123!")
    DEFAULT_USER_USERNAME = os.getenv("DEFAULT_USER_USERNAME", "demouser")
    
    # Rate Limiting
    RATELIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "100 per minute")
    RATELIMIT_STORAGE_URI = "memory://"
    
    # NLP Processing Limits
    MAX_INPUT_TEXT_LENGTH = int(os.getenv("MAX_INPUT_TEXT_LENGTH", "50000"))
    
    # Provider Settings
    TRANSLATION_PROVIDER = os.getenv("TRANSLATION_PROVIDER", "mock")
    TRANSLATION_API_KEY = os.getenv("TRANSLATION_API_KEY", "")
    REWRITING_PROVIDER = os.getenv("REWRITING_PROVIDER", "rule_based")
    REWRITING_API_KEY = os.getenv("REWRITING_API_KEY", "")
    QA_PROVIDER = os.getenv("QA_PROVIDER", "extractive")
    QA_API_KEY = os.getenv("QA_API_KEY", "")

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    RATELIMIT_ENABLED = False
    TRANSLATION_PROVIDER = "mock"

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
