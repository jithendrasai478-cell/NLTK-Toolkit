from typing import Any, Dict, List, Optional
from flask import request
from backend.utils.error_handlers import APIException

def validate_json_body() -> Dict[str, Any]:
    """Ensure request has valid JSON body."""
    if not request.is_json:
        raise APIException("INVALID_CONTENT_TYPE", "Request body must be valid application/json.", status_code=400)
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        raise APIException("MALFORMED_JSON", "Request body must be a valid JSON object.", status_code=400)
    return data

def validate_text_input(
    data: Dict[str, Any], 
    field_name: str = "text", 
    min_len: int = 1, 
    max_len: int = 50000
) -> str:
    """Validate and sanitize a text input string."""
    if field_name not in data:
        raise APIException("MISSING_FIELD", f"Field '{field_name}' is required.", status_code=400)
    
    val = data[field_name]
    if not isinstance(val, str):
        raise APIException("INVALID_TYPE", f"Field '{field_name}' must be a string.", status_code=400)
    
    cleaned = val.strip()
    if len(cleaned) < min_len:
        raise APIException("EMPTY_INPUT", f"Field '{field_name}' cannot be empty or only whitespace.", status_code=400)
        
    if len(cleaned) > max_len:
        raise APIException(
            "INPUT_TOO_LONG", 
            f"Field '{field_name}' length ({len(cleaned)} chars) exceeds maximum limit of {max_len} characters.", 
            status_code=413
        )
        
    return cleaned

def validate_choice(val: Any, allowed: List[Any], field_name: str = "option") -> Any:
    """Validate that a field value is among allowed options."""
    if val not in allowed:
        raise APIException(
            "INVALID_CHOICE", 
            f"Field '{field_name}' must be one of: {allowed}. Received: '{val}'.", 
            status_code=400
        )
    return val

def validate_int_range(val: Any, min_val: int, max_val: int, field_name: str = "number") -> int:
    """Validate that a field is an integer within [min_val, max_val]."""
    try:
        num = int(val)
    except (ValueError, TypeError):
        raise APIException("INVALID_INTEGER", f"Field '{field_name}' must be an integer.", status_code=400)
    if num < min_val or num > max_val:
        raise APIException(
            "OUT_OF_RANGE", 
            f"Field '{field_name}' must be between {min_val} and {max_val}. Received: {num}.", 
            status_code=400
        )
    return num
