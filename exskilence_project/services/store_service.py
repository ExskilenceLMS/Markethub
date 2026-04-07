from typing import Any, Dict, List, Optional

from exceptions import NotFoundException, ValidationException
from models.user import ROLE_SELLER
from repositories.category_repository import CategoryRepository
from repositories.store_repository import StoreRepository
from repositories.user_repository import UserRepository
from validators.store_validator import parse_store_form


class StoreService:
    def __init__(
        self,
        store_repository: Optional[StoreRepository] = None,
        user_repository: Optional[UserRepository] = None,
        category_repository: Optional[CategoryRepository] = None,
    ):
        self._store = store_repository or StoreRepository()
        self._users = user_repository or UserRepository()
        self._cat = category_repository or CategoryRepository()

    def _ensure_seller(self, seller_id: int) -> None:
        u = self._users.get_by_id(seller_id)
        if u is None or u.role != ROLE_SELLER:
            raise ValidationException(
                "Assigned user must be an active seller account",
                details=["seller_id"],
            )

    def list_all_dicts(self) -> List[Dict[str, Any]]:
        return [s.to_dict(include_categories=True) for s in self._store.list_all_with_relations()]

    def list_for_seller(self, seller_user_id: int) -> List[Dict[str, Any]]:
        return [
            s.to_dict(include_categories=True)
            for s in self._store.list_by_seller_id(seller_user_id)
        ]

    def get_dict(self, store_id: int) -> Dict[str, Any]:
        s = self._store.get_by_id(store_id)
        if s is None:
            raise NotFoundException("Store not found")
        return s.to_dict(include_categories=True)

    def list_sellers_for_dropdown(self) -> List[Dict[str, Any]]:
        return [
            {"id": u.id, "name": u.name, "email": u.email}
            for u in self._users.list_users_by_role(ROLE_SELLER)
        ]

    def staff_assignments_overview(self) -> List[Dict[str, Any]]:
        rows = []
        for u in self._users.list_users_by_role(ROLE_SELLER):
            stores = self._store.list_by_seller_id(u.id)
            rows.append(
                {
                    "seller_id": u.id,
                    "seller_name": u.name,
                    "seller_email": u.email,
                    "stores": [s.to_dict(include_categories=True) for s in stores],
                }
            )
        return rows

    def create(self, form_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        name, seller_id, is_active, category_ids = parse_store_form(form_data)
        self._ensure_seller(seller_id)
        for cid in category_ids:
            if self._cat.get_by_id(cid) is None:
                raise ValidationException("One or more categories are invalid", details=["category_ids"])
        s = self._store.create(name, seller_id, is_active, category_ids)
        return s.to_dict(include_categories=True)

    def update(self, store_id: int, form_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        s = self._store.get_by_id(store_id)
        if s is None:
            raise NotFoundException("Store not found")
        name, seller_id, is_active, category_ids = parse_store_form(form_data)
        self._ensure_seller(seller_id)
        for cid in category_ids:
            if self._cat.get_by_id(cid) is None:
                raise ValidationException("One or more categories are invalid", details=["category_ids"])
        self._store.update(s, name, seller_id, is_active, category_ids)
        return s.to_dict(include_categories=True)

    def delete(self, store_id: int) -> None:
        s = self._store.get_by_id(store_id)
        if s is None:
            raise NotFoundException("Store not found")
        self._store.delete(s)
