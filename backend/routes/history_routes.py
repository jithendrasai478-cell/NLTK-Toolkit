from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db
from backend.models.history import History
from backend.models.favorite import Favorite
from backend.utils.error_handlers import api_success, APIException
from backend.utils.validators import validate_json_body

history_bp = Blueprint("history", __name__, url_prefix="/api/v1")

@history_bp.route("/history", methods=["GET"])
def get_history():
    """Get recent processing history (guest or authenticated)."""
    limit = min(50, int(request.args.get("limit", 20)))
    query = History.query.order_by(History.created_at.desc()).limit(limit)
    items = [h.to_dict() for h in query.all()]
    return api_success({"history": items, "count": len(items)})

@history_bp.route("/history", methods=["POST"])
def add_history():
    """Save an execution audit event."""
    data = validate_json_body()
    tool_name = data.get("tool_name", "nlp_tool").strip()
    input_snippet = data.get("input_snippet", "")[:250].strip()
    output_summary = data.get("output_summary", "")[:500].strip()
    ms = float(data.get("processing_time_ms", 0.0))

    history_item = History(
        tool_name=tool_name,
        input_snippet=input_snippet,
        output_summary=output_summary,
        processing_time_ms=ms
    )
    db.session.add(history_item)
    db.session.commit()
    return api_success({"history_item": history_item.to_dict()}, status_code=201)

@history_bp.route("/history/<int:history_id>", methods=["DELETE"])
def delete_single_history(history_id: int):
    item = db.session.get(History, history_id)
    if not item:
        raise APIException("NOT_FOUND", f"History item {history_id} not found.", status_code=404)
    db.session.delete(item)
    db.session.commit()
    return api_success({"deleted_id": history_id, "message": "History entry deleted."})

@history_bp.route("/history", methods=["DELETE"])
def clear_all_history():
    deleted_count = History.query.delete()
    db.session.commit()
    return api_success({"deleted_count": deleted_count, "message": "All history cleared."})

@history_bp.route("/favorites", methods=["GET"])
def get_favorites():
    favs = Favorite.query.order_by(Favorite.created_at.desc()).all()
    return api_success({"favorites": [f.to_dict() for f in favs]})

@history_bp.route("/favorites", methods=["POST"])
def toggle_favorite():
    data = validate_json_body()
    tool_id = data.get("tool_id", "").strip()
    user_id = int(data.get("user_id", 1))

    existing = Favorite.query.filter_by(user_id=user_id, tool_id=tool_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return api_success({"favorited": False, "tool_id": tool_id})
    else:
        fav = Favorite(user_id=user_id, tool_id=tool_id)
        db.session.add(fav)
        db.session.commit()
        return api_success({"favorited": True, "tool_id": tool_id, "favorite": fav.to_dict()})
