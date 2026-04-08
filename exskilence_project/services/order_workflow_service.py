from typing import Any, Dict, Optional

from repositories.cart_repository import CartRepository
from services.cart_service import CartService
from services.inventory_service import InventoryService
from services.order_service import OrderService


class OrderWorkflowService:
    """
    Orchestrates order placement across cart, inventory, and order services.
    """

    def __init__(
        self,
        cart_service: Optional[CartService] = None,
        inventory_service: Optional[InventoryService] = None,
        order_service: Optional[OrderService] = None,
        cart_repository: Optional[CartRepository] = None,
    ):
        self._cart_service = cart_service or CartService()
        self._inventory = inventory_service or InventoryService()
        self._orders = order_service or OrderService()
        self._cart_repo = cart_repository or CartRepository()

    def place_order_from_cart(self, user_id: int) -> Dict[str, Any]:
        self._orders.ensure_user_exists(user_id)
        _, total = self._cart_service.get_cart_summary(user_id)
        rows = self._cart_repo.list_by_user_id(user_id)
        self._inventory.ensure_cart_items_have_stock(rows)
        return self._orders.create_order_from_validated_cart(user_id, total, rows)
