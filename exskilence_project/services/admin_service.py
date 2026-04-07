from typing import Any, Dict, Optional

from models.user import ROLE_ADMIN, ROLE_CUSTOMER, ROLE_SELLER
from repositories.user_repository import UserRepository


class AdminService:
    def __init__(self, user_repository: Optional[UserRepository] = None):
        self._users = user_repository or UserRepository()

    def get_dashboard_stats(self) -> Dict[str, Any]:
        return {
            "total_users": self._users.count_all_users(),
            "total_admins": self._users.count_users_with_role(ROLE_ADMIN),
            "total_sellers": self._users.count_users_with_role(ROLE_SELLER),
            "total_customers": self._users.count_users_with_role(ROLE_CUSTOMER),
            "total_products": 0,
            "total_orders": 0,
        }
