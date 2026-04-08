from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models import db
from models.cart_item import CartItem


class CartRepository:
    def get_by_id_for_user(self, line_id: int, user_id: int) -> Optional[CartItem]:
        stmt = (
            select(CartItem)
            .where(CartItem.id == line_id, CartItem.user_id == user_id)
            .options(selectinload(CartItem.product))
        )
        return db.session.execute(stmt).scalar_one_or_none()

    def get_by_user_and_product(self, user_id: int, product_id: int) -> Optional[CartItem]:
        stmt = select(CartItem).where(
            CartItem.user_id == user_id,
            CartItem.product_id == product_id,
        )
        return db.session.execute(stmt).scalar_one_or_none()

    def list_by_user_id(self, user_id: int) -> List[CartItem]:
        stmt = (
            select(CartItem)
            .where(CartItem.user_id == user_id)
            .options(selectinload(CartItem.product))
            .order_by(CartItem.created_at.asc())
        )
        return list(db.session.scalars(stmt).unique().all())

    def add_item(self, user_id: int, product_id: int, quantity: int) -> CartItem:
        existing = self.get_by_user_and_product(user_id, product_id)
        try:
            if existing:
                existing.quantity = existing.quantity + quantity
                db.session.commit()
                return self.get_by_id_for_user(existing.id, user_id)  # type: ignore
            row = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
            db.session.add(row)
            db.session.flush()
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return self.get_by_id_for_user(row.id, user_id)  # type: ignore

    def update_quantity(self, item: CartItem, quantity: int) -> CartItem:
        item.quantity = quantity
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return self.get_by_id_for_user(item.id, item.user_id)  # type: ignore

    def remove_item(self, item: CartItem) -> None:
        try:
            db.session.delete(item)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def clear_for_user(self, user_id: int) -> None:
        rows = self.list_by_user_id(user_id)
        try:
            for r in rows:
                db.session.delete(r)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
