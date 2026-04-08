from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from exceptions import ValidationException
from models import db
from models.cart_item import CartItem
from models.order import Order
from validators.order_validator import STATUS_PLACED


class OrderRepository:
    def create(self, user_id: int, total_amount: Decimal, status: str = STATUS_PLACED) -> Order:
        o = Order(user_id=user_id, total_amount=total_amount, status=status)
        try:
            db.session.add(o)
            db.session.flush()
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return self.get_by_id(o.id)  # type: ignore

    def create_from_cart_lines(
        self,
        user_id: int,
        total_amount: Decimal,
        lines: List[CartItem],
    ) -> Order:
        """
        Single transaction: insert order, decrement product stock for each line,
        remove cart lines. Includes defensive stock checks to avoid overselling
        if inventory changes between validation and commit.
        """
        if not lines:
            raise ValueError("lines must not be empty")
        try:
            order = Order(user_id=user_id, total_amount=total_amount, status=STATUS_PLACED)
            db.session.add(order)
            db.session.flush()
            for line in lines:
                prod = line.product
                if prod is None:
                    raise ValidationException("Product does not exist", details=["_form"])
                if line.quantity > prod.quantity:
                    raise ValidationException(
                        f"Insufficient stock for {prod.name}",
                        details=["_form"],
                    )
                prod.quantity = prod.quantity - line.quantity
            for line in lines:
                db.session.delete(line)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return self.get_by_id(order.id)  # type: ignore

    def get_by_id(self, order_id: int) -> Optional[Order]:
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.user))
        )
        return db.session.execute(stmt).scalar_one_or_none()

    def list_by_user_id(self, user_id: int) -> List[Order]:
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.user))
            .order_by(Order.created_at.desc())
        )
        return list(db.session.scalars(stmt).unique().all())

    def list_all_ordered(self) -> List[Order]:
        stmt = (
            select(Order)
            .options(selectinload(Order.user))
            .order_by(Order.created_at.desc())
        )
        return list(db.session.scalars(stmt).unique().all())

    def update_status(self, order: Order, status: str) -> Order:
        order.status = status
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return self.get_by_id(order.id)  # type: ignore
