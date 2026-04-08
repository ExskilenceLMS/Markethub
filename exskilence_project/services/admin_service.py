from typing import Any, Dict, Optional

from sqlalchemy import func, select

from models import db
from models.category import Category
from models.order import Order
from models.product import Product
from models.store import Store
from models.user import ROLE_ADMIN, ROLE_CUSTOMER, ROLE_SELLER
from repositories.user_repository import UserRepository


class AdminService:
    def __init__(self, user_repository: Optional[UserRepository] = None):
        self._users = user_repository or UserRepository()

    @staticmethod
    def _count_rows(model) -> int:
        n = db.session.scalar(select(func.count(model.id)))
        return int(n or 0)

    def get_dashboard_stats(self) -> Dict[str, Any]:
        return {
            "total_users": self._users.count_all_users(),
            "total_admins": self._users.count_users_with_role(ROLE_ADMIN),
            "total_sellers": self._users.count_users_with_role(ROLE_SELLER),
            "total_customers": self._users.count_users_with_role(ROLE_CUSTOMER),
            "total_categories": self._count_rows(Category),
            "total_stores": self._count_rows(Store),
            "total_products": self._count_rows(Product),
            "total_orders": self._count_rows(Order),
        }
