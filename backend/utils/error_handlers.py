import time
from typing import Any, Dict, Optional
from flask import jsonify, Response

def api_success(data: Any = None, meta: Optional[Dict[str, Any]] = None, status_code: int = 200) -> Response:
    """Standardized successful JSON response envelope."""
    payload: Dict[str, Any] = {
        "success": True,
        "data": data if data is not None else {}
    }
    if meta is not None:
        payload["meta"] = meta
    return jsonify(payload), status_code

def api_error(code: str, message: str, details: Optional[Any] = None, status_code: int = 400) -> Response:
    """Standardized error JSON response envelope."""
    payload: Dict[str, Any] = {
        "success": False,
        "message": message,
        "error": {
            "code": code,
            "message": message,
        }
    }
    if details is not None:
        payload["error"]["details"] = details
    return jsonify(payload), status_code

class APIException(Exception):
    """Custom API Exception for domain services."""
    def __init__(self, code: str, message: str, status_code: int = 400, details: Optional[Any] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details

def register_error_handlers(app):
    """Register application-wide HTTP and API exception handlers."""
    from werkzeug.exceptions import HTTPException
    
    @app.errorhandler(APIException)
    def handle_api_exception(e: APIException):
        return api_error(e.code, e.message, e.details, e.status_code)

    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):
        code = getattr(e, 'code', 500)
        name = getattr(e, 'name', 'HTTP_ERROR').upper().replace(' ', '_')
        desc = getattr(e, 'description', str(e))
        return api_error(name, desc, status_code=code)

    @app.errorhandler(400)
    def bad_request(e):
        return api_error("BAD_REQUEST", str(e.description if hasattr(e, 'description') else "Bad Request"), status_code=400)

    @app.errorhandler(401)
    def unauthorized(e):
        return api_error("UNAUTHORIZED", str(e.description if hasattr(e, 'description') else "Unauthorized"), status_code=401)

    @app.errorhandler(403)
    def forbidden(e):
        return api_error("FORBIDDEN", str(e.description if hasattr(e, 'description') else "Forbidden"), status_code=403)

    @app.errorhandler(404)
    def not_found(e):
        return api_error("NOT_FOUND", "The requested resource was not found.", status_code=404)

    @app.errorhandler(405)
    def method_not_allowed(e):
        return api_error("METHOD_NOT_ALLOWED", "The HTTP method is not allowed for this endpoint.", status_code=405)

    @app.errorhandler(413)
    def payload_too_large(e):
        return api_error("PAYLOAD_TOO_LARGE", "The request payload exceeds the allowed limit.", status_code=413)

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return api_error("RATE_LIMIT_EXCEEDED", "Too many requests. Please slow down and try again later.", status_code=429)

    @app.errorhandler(500)
    def internal_error(e):
        return api_error("INTERNAL_SERVER_ERROR", "An unexpected server error occurred. Please try again later.", status_code=500)

    @app.errorhandler(Exception)
    def handle_unexpected_exception(e: Exception):
        app.logger.exception("Unhandled server exception: %s", str(e))
        return api_error(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected server error occurred. Please try again later.",
            details=str(e) if app.config.get("DEBUG") else None,
            status_code=500
        )
