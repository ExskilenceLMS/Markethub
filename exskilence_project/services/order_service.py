from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from exceptions import AuthorizationException, NotFoundException, ValidationException
from models.user import ROLE_ADMIN, ROLE_CUSTOMER, ROLE_SELLER
from repositories.cart_repository import CartRepository
from repositories.order_repository import OrderRepository
from repositories.user_repository import UserRepository
from services.cart_service import CartService
from validators.order_validator import (
    assert_valid_status_transition,
    next_status_choices,
    parse_order_status_update,
)


class OrderService:
    def __init__(
        self,
        order_repository: Optional[OrderRepository] = None,
        cart_repository: Optional[CartRepository] = None,
        user_repository: Optional[UserRepository] = None,
        cart_service: Optional[CartService] = None,
    ):
        self._orders = order_repository or OrderRepository()
        self._cart = cart_repository or CartRepository()
        self._users = user_repository or UserRepository()
        self._cart_service = cart_service or CartService()

    def place_from_cart(self, user_id: int) -> Dict[str, Any]:
        if self._users.get_by_id(user_id) is None:
            raise ValidationException("User does not exist", details=["_form"])
        _, total = self._cart_service.get_cart_summary(user_id)
        rows = self._cart.list_by_user_id(user_id)
        if not rows:
            raise ValidationException("Cart is empty", details=["_form"])
        for row in rows:
            p = row.product
            if p is None:
                raise ValidationException("Invalid cart contents", details=["_form"])
            if p.quantity < row.quantity:
                raise ValidationException(
                    f"Insufficient stock for {p.name}",
                    details=["_form"],
                )
        order = self._orders.create_from_cart_lines(user_id, total, rows)
        return order.to_dict()

    def list_dicts_for_role(self, role: str, acting_user_id: int) -> List[Dict[str, Any]]:
        if role in (ROLE_ADMIN, ROLE_SELLER):
            items = self._orders.list_all_ordered()
        elif role == ROLE_CUSTOMER:
            items = self._orders.list_by_user_id(acting_user_id)
        else:
            items = []
        return [o.to_dict() for o in items]

    def get_dict(self, order_id: int, acting_user_id: int, acting_role: str) -> Dict[str, Any]:
        o = self._orders.get_by_id(order_id)
        if o is None:
            raise NotFoundException("Order not found")
        if acting_role == ROLE_CUSTOMER and o.user_id != acting_user_id:
            raise AuthorizationException("You can only view your own orders")
        return o.to_dict()

    def get_dict_with_next_statuses(
        self, order_id: int, acting_user_id: int, acting_role: str
    ) -> Tuple[Dict[str, Any], List[str]]:
        d = self.get_dict(order_id, acting_user_id, acting_role)
        choices = next_status_choices(d["status"])
        return d, choices

    def update_status(
        self,
        order_id: int,
        form_data: Optional[Dict[str, Any]],
        acting_role: str,
    ) -> Dict[str, Any]:
        if acting_role not in (ROLE_ADMIN, ROLE_SELLER):
            raise AuthorizationException("Not allowed to update order status")
        new_status = parse_order_status_update(form_data)
        o = self._orders.get_by_id(order_id)
        if o is None:
            raise NotFoundException("Order not found")
        assert_valid_status_transition(o.status, new_status)
        o = self._orders.update_status(o, new_status)
        return o.to_dict()
