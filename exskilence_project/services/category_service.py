from typing import Any, Dict, List, Optional

from exceptions import NotFoundException, ValidationException
from repositories.category_repository import CategoryRepository
from repositories.store_repository import StoreRepository
from repositories.user_repository import UserRepository
from validators.category_validator import parse_category_form


class CategoryService:
    def __init__(
        self,
        category_repository: Optional[CategoryRepository] = None,
        store_repository: Optional[StoreRepository] = None,
        user_repository: Optional[UserRepository] = None,
    ):
        self._cat = category_repository or CategoryRepository()
        self._store = store_repository or StoreRepository()
        self._users = user_repository or UserRepository()

    def list_all_dicts(self) -> List[Dict[str, Any]]:
        return [c.to_dict() for c in self._cat.list_all_ordered()]

    def list_for_seller(self, seller_user_id: int) -> List[Dict[str, Any]]:
        stores = self._store.list_by_seller_id(seller_user_id)
        seen = {}
        for s in stores:
            for c in s.categories:
                seen[c.id] = c
        return [c.to_dict() for c in sorted(seen.values(), key=lambda x: x.name)]

    def get_dict(self, category_id: int) -> Dict[str, Any]:
        c = self._cat.get_by_id(category_id)
        if c is None:
            raise NotFoundException("Category not found")
        return c.to_dict()

    def create(self, form_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        name, description = parse_category_form(form_data)
        existing = self._cat.get_by_name(name)
        if existing is not None:
            raise ValidationException("A category with this name already exists", details=["name"])
        c = self._cat.create(name, description)
        return c.to_dict()

    def update(self, category_id: int, form_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        c = self._cat.get_by_id(category_id)
        if c is None:
            raise NotFoundException("Category not found")
        name, description = parse_category_form(form_data)
        other = self._cat.get_by_name(name)
        if other is not None and other.id != c.id:
            raise ValidationException("A category with this name already exists", details=["name"])
        self._cat.update(c, name, description)
        return c.to_dict()

    def delete(self, category_id: int) -> None:
        c = self._cat.get_by_id(category_id)
        if c is None:
            raise NotFoundException("Category not found")
        self._cat.delete(c)
