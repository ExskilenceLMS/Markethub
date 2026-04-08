from typing import Any, Dict, List, Optional

from exceptions import AuthorizationException, NotFoundException, ValidationException
from models.user import ROLE_ADMIN, ROLE_SELLER
from repositories.category_repository import CategoryRepository
from repositories.product_repository import ProductRepository
from repositories.user_repository import UserRepository
from validators.product_validator import parse_product_payload


class ProductService:
    def __init__(
        self,
        product_repository: Optional[ProductRepository] = None,
        category_repository: Optional[CategoryRepository] = None,
        user_repository: Optional[UserRepository] = None,
    ):
        self._products = product_repository or ProductRepository()
        self._categories = category_repository or CategoryRepository()
        self._users = user_repository or UserRepository()

    def _ensure_category(self, category_id: int) -> None:
        if self._categories.get_by_id(category_id) is None:
            raise ValidationException("Category does not exist", details=["category_id"])

    def _ensure_seller(self, seller_id: int) -> None:
        u = self._users.get_by_id(seller_id)
        if u is None or u.role != ROLE_SELLER:
            raise ValidationException("Invalid seller", details=["seller_id"])

    def _can_modify(self, seller_id: int, acting_user_id: int, acting_role: str) -> None:
        if acting_role == ROLE_ADMIN:
            return
        if acting_role == ROLE_SELLER and seller_id == acting_user_id:
            return
        raise AuthorizationException("You can only manage your own products")

    def list_for_role(self, acting_role: str, acting_user_id: int) -> List[Dict[str, Any]]:
        if acting_role == ROLE_ADMIN:
            items = self._products.list_all_ordered()
        elif acting_role == ROLE_SELLER:
            items = self._products.list_by_seller_id(acting_user_id)
        else:
            items = self._products.list_all_ordered()
        return [p.to_dict() for p in items]

    def get_dict(self, product_id: int) -> Dict[str, Any]:
        p = self._products.get_by_id(product_id)
        if p is None:
            raise NotFoundException("Product not found")
        return p.to_dict()

    def create(
        self,
        form_data: Optional[Dict[str, Any]],
        acting_user_id: int,
        acting_role: str,
    ) -> Dict[str, Any]:
        require_seller = acting_role == ROLE_ADMIN
        name, description, price, quantity, category_id, seller_id_form, image_url = (
            parse_product_payload(form_data, require_seller_id=require_seller)
        )
        self._ensure_category(category_id)

        if acting_role == ROLE_ADMIN:
            sid = seller_id_form
            if sid is None:
                raise ValidationException("Seller is required", details=["seller_id"])
            self._ensure_seller(sid)
            seller_id = sid
        elif acting_role == ROLE_SELLER:
            seller_id = acting_user_id
        else:
            raise AuthorizationException("Only admin or seller can create products")

        p = self._products.create(
            name, description, price, quantity, category_id, seller_id, image_url
        )
        return p.to_dict()

    def update(
        self,
        product_id: int,
        form_data: Optional[Dict[str, Any]],
        acting_user_id: int,
        acting_role: str,
    ) -> Dict[str, Any]:
        p = self._products.get_by_id(product_id)
        if p is None:
            raise NotFoundException("Product not found")
        self._can_modify(p.seller_id, acting_user_id, acting_role)

        require_seller = acting_role == ROLE_ADMIN
        name, description, price, quantity, category_id, seller_id_form, image_url = (
            parse_product_payload(form_data, require_seller_id=require_seller)
        )
        self._ensure_category(category_id)

        if acting_role == ROLE_ADMIN:
            sid = seller_id_form
            if sid is None:
                raise ValidationException("Seller is required", details=["seller_id"])
            self._ensure_seller(sid)
            seller_id = sid
        else:
            seller_id = p.seller_id

        p = self._products.update(
            p, name, description, price, quantity, category_id, seller_id, image_url
        )
        return p.to_dict()

    def delete(self, product_id: int, acting_user_id: int, acting_role: str) -> None:
        p = self._products.get_by_id(product_id)
        if p is None:
            raise NotFoundException("Product not found")
        if acting_role not in (ROLE_ADMIN, ROLE_SELLER):
            raise AuthorizationException("Not allowed to delete products")
        self._can_modify(p.seller_id, acting_user_id, acting_role)
        self._products.delete(p)
