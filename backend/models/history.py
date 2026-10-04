from datetime import datetime, timezone
from backend.extensions import db

class History(db.Model):
    __tablename__ = "history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    tool_name = db.Column(db.String(64), nullable=False, index=True)
    input_snippet = db.Column(db.String(256), nullable=False)
    output_summary = db.Column(db.String(512), nullable=False)
    processing_time_ms = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "tool_name": self.tool_name,
            "input_snippet": self.input_snippet,
            "output_summary": self.output_summary,
            "processing_time_ms": self.processing_time_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
