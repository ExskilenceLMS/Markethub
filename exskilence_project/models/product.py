from datetime import datetime
from decimal import Decimal

from models.db import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False, index=True)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    image_url = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    category = db.relationship("Category", backref=db.backref("products", lazy="dynamic"))
    seller = db.relationship("User", backref=db.backref("products", lazy="dynamic"))

    def to_dict(self):
        price_val = self.price
        if isinstance(price_val, Decimal):
            price_val = float(price_val)
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description or "",
            "price": price_val,
            "quantity": self.quantity,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else "",
            "seller_id": self.seller_id,
            "seller_name": self.seller.name if self.seller else "",
            "seller_email": self.seller.email if self.seller else "",
            "image_url": self.image_url or "",
            "created_at": self.created_at.isoformat() + "Z" if self.created_at else None,
        }
