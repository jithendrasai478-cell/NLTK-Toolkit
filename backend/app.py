import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify

BASE_DIR = Path(__file__).resolve().parent
# Ensure project root is in sys.path so "backend.xxx" imports work regardless of CWD
if str(BASE_DIR.parent) not in sys.path:
    sys.path.insert(0, str(BASE_DIR.parent))

env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)
root_env_path = BASE_DIR.parent / ".env"
if root_env_path.exists():
    load_dotenv(root_env_path, override=False)

from backend.config import config_by_name
from backend.extensions import db, migrate, cors, jwt, limiter
from backend.utils.error_handlers import register_error_handlers
from backend.routes.health_routes import health_bp
from backend.routes.nlp_routes import nlp_bp
from backend.routes.auth_routes import auth_bp
from backend.routes.history_routes import history_bp
from backend.routes.learning_routes import learning_bp

def create_app(config_name: str = None) -> Flask:
    """Application factory pattern for Flask."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Safe diagnostic logging (Do NOT print actual Client ID or secrets)
    client_id_configured = bool(app.config.get("GOOGLE_CLIENT_ID") and app.config.get("GOOGLE_CLIENT_ID") != "YOUR_GOOGLE_CLIENT_ID")
    app.logger.info("Google Client ID configured: %s", client_id_configured)
    print(f"Google Client ID configured: {client_id_configured}")

    # Initialize extensions
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["FRONTEND_ORIGINS"]}})
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)

    # Register error handlers
    register_error_handlers(app)

    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(nlp_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(learning_bp)

    # Create tables for SQLite if not exist and seed/sync configurable user
    with app.app_context():
        import backend.models  # noqa
        db.create_all()

        # Ensure google_id, display_name, and avatar_url columns exist for existing SQLite databases
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            existing_cols = [col["name"] for col in inspector.get_columns("users")]
            with db.engine.connect() as conn:
                if "google_id" not in existing_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN google_id VARCHAR(128)"))
                if "avatar_url" not in existing_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR(512)"))
                if "display_name" not in existing_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN display_name VARCHAR(128)"))
                conn.commit()
        except Exception as e:
            app.logger.debug(f"User schema check: {e}")

        from backend.models.user import User
        default_email = app.config.get("DEFAULT_USER_EMAIL")
        default_password = app.config.get("DEFAULT_USER_PASSWORD")
        default_username = app.config.get("DEFAULT_USER_USERNAME", "demouser")
        if default_email and default_password:
            email_clean = default_email.strip().lower()
            user = User.query.filter_by(email=email_clean).first()
            if not user:
                user = User.query.filter_by(username=default_username).first()
            if not user:
                user = User(username=default_username, email=email_clean)
                user.set_password(default_password)
                db.session.add(user)
                db.session.commit()
            else:
                user.email = email_clean
                if not user.check_password(default_password):
                    user.set_password(default_password)
                db.session.commit()

    @app.route("/")
    def root():
        return jsonify({
            "name": "NLTK Toolkit API",
            "version": "1.0.0",
            "documentation": "/api/v1/health",
            "status": "online"
        })

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(app.config.get("PORT") or os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", False))
