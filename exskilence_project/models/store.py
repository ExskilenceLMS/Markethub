from datetime import datetime

from models.db import db

store_categories = db.Table(
    "store_categories",
    db.Column("store_id", db.Integer, db.ForeignKey("stores.id", ondelete="CASCADE"), primary_key=True),
    db.Column(
        "category_id",
        db.Integer,
        db.ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Store(db.Model):
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    seller = db.relationship("User", backref=db.backref("stores", lazy="dynamic"))
    categories = db.relationship(
        "Category",
        secondary=store_categories,
        lazy="joined",
        backref=db.backref("stores", lazy="dynamic"),
    )

    def to_dict(self, include_categories=False):
        d = {
            "id": self.id,
            "name": self.name,
            "seller_id": self.seller_id,
            "seller_name": self.seller.name if self.seller else "",
            "seller_email": self.seller.email if self.seller else "",
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() + "Z" if self.created_at else None,
        }
        if include_categories:
            d["categories"] = [c.to_dict() for c in self.categories]
            d["category_ids"] = [c.id for c in self.categories]
        return d
