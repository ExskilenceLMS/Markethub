from typing import List

from exceptions import ValidationException
from models.cart_item import CartItem
from validators.inventory_validator import validate_requested_quantity


class InventoryService:
    def ensure_cart_items_have_stock(self, cart_rows: List[CartItem]) -> None:
        if not cart_rows:
            raise ValidationException("Cart is empty", details=["_form"])

        for row in cart_rows:
            product = row.product
            if product is None:
                raise ValidationException("Product does not exist", details=["_form"])
            validate_requested_quantity(row.quantity)
            if row.quantity > product.quantity:
                raise ValidationException(
                    f"Insufficient stock for {product.name}",
                    details=["_form"],
                )
