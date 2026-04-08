from datetime import datetime
from decimal import Decimal

from models.db import db


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.String(32), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("orders", lazy="dynamic"))

    def to_dict(self):
        ta = self.total_amount
        if isinstance(ta, Decimal):
            ta = float(ta)
        return {
            "id": self.id,
            "user_id": self.user_id,
            "customer_name": self.user.name if self.user else "",
            "customer_email": self.user.email if self.user else "",
            "total_amount": ta,
            "status": self.status,
            "created_at": self.created_at.isoformat() + "Z" if self.created_at else None,
        }
