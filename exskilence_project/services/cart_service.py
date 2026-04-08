from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from exceptions import NotFoundException, ValidationException
from repositories.cart_repository import CartRepository
from repositories.product_repository import ProductRepository
from validators.cart_validator import parse_cart_line_quantity, parse_cart_product_quantity


class CartService:
    def __init__(
        self,
        cart_repository: Optional[CartRepository] = None,
        product_repository: Optional[ProductRepository] = None,
    ):
        self._cart = cart_repository or CartRepository()
        self._products = product_repository or ProductRepository()

    def _ensure_product(self, product_id: int) -> None:
        if self._products.get_by_id(product_id) is None:
            raise ValidationException("Product does not exist", details=["product_id"])

    def add(self, user_id: int, form_data: Optional[Dict[str, Any]]) -> None:
        product_id, quantity = parse_cart_product_quantity(form_data)
        self._ensure_product(product_id)
        self._cart.add_item(user_id, product_id, quantity)

    def update_line(self, user_id: int, line_id: int, form_data: Optional[Dict[str, Any]]) -> None:
        qty = parse_cart_line_quantity(form_data)
        item = self._cart.get_by_id_for_user(line_id, user_id)
        if item is None:
            raise NotFoundException("Cart item not found")
        self._cart.update_quantity(item, qty)

    def remove_line(self, user_id: int, line_id: int) -> None:
        item = self._cart.get_by_id_for_user(line_id, user_id)
        if item is None:
            raise NotFoundException("Cart item not found")
        self._cart.remove_item(item)

    def clear(self, user_id: int) -> None:
        self._cart.clear_for_user(user_id)

    def _line_amount(self, unit_price: Any, quantity: int) -> Decimal:
        if isinstance(unit_price, Decimal):
            d = unit_price
        else:
            d = Decimal(str(unit_price))
        return d * quantity

    def get_cart_summary(self, user_id: int) -> Tuple[List[Dict[str, Any]], Decimal]:
        rows = self._cart.list_by_user_id(user_id)
        items: List[Dict[str, Any]] = []
        total = Decimal("0")
        for row in rows:
            p = row.product
            if p is None:
                continue
            unit = p.price
            if not isinstance(unit, Decimal):
                unit = Decimal(str(unit))
            line_total = self._line_amount(unit, row.quantity)
            total += line_total
            price_f = float(unit) if isinstance(unit, Decimal) else float(unit)
            items.append(
                {
                    "id": row.id,
                    "product_id": row.product_id,
                    "name": p.name,
                    "price": price_f,
                    "quantity": row.quantity,
                    "line_total": float(line_total),
                    "image_url": p.image_url or "",
                }
            )
        return items, total
