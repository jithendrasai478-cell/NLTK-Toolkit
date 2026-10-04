from datetime import datetime, timezone
from backend.extensions import db

class Favorite(db.Model):
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    tool_id = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint("user_id", "tool_id", name="unique_user_favorite"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "tool_id": self.tool_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
