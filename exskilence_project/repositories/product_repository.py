from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models import db
from models.product import Product


class ProductRepository:
    def create(
        self,
        name: str,
        description: Optional[str],
        price: Decimal,
        quantity: int,
        category_id: int,
        seller_id: int,
        image_url: Optional[str],
    ) -> Product:
        p = Product(
            name=name,
            description=description,
            price=price,
            quantity=quantity,
            category_id=category_id,
            seller_id=seller_id,
            image_url=image_url,
        )
        try:
            db.session.add(p)
            db.session.flush()
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return self.get_by_id(p.id)  # type: ignore

    def get_by_id(self, product_id: int) -> Optional[Product]:
        stmt = (
            select(Product)
            .where(Product.id == product_id)
            .options(selectinload(Product.category), selectinload(Product.seller))
        )
        return db.session.execute(stmt).scalar_one_or_none()

    def list_all_ordered(self) -> List[Product]:
        stmt = (
            select(Product)
            .options(selectinload(Product.category), selectinload(Product.seller))
            .order_by(Product.created_at.desc())
        )
        return list(db.session.scalars(stmt).unique().all())

    def list_by_seller_id(self, seller_id: int) -> List[Product]:
        stmt = (
            select(Product)
            .where(Product.seller_id == seller_id)
            .options(selectinload(Product.category), selectinload(Product.seller))
            .order_by(Product.created_at.desc())
        )
        return list(db.session.scalars(stmt).unique().all())

    def list_by_category_id(self, category_id: int) -> List[Product]:
        stmt = (
            select(Product)
            .where(Product.category_id == category_id)
            .options(selectinload(Product.category), selectinload(Product.seller))
            .order_by(Product.created_at.desc())
        )
        return list(db.session.scalars(stmt).unique().all())

    def update(
        self,
        product: Product,
        name: str,
        description: Optional[str],
        price: Decimal,
        quantity: int,
        category_id: int,
        seller_id: int,
        image_url: Optional[str],
    ) -> Product:
        product.name = name
        product.description = description
        product.price = price
        product.quantity = quantity
        product.category_id = category_id
        product.seller_id = seller_id
        product.image_url = image_url
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return self.get_by_id(product.id)  # type: ignore

    def delete(self, product: Product) -> None:
        try:
            db.session.delete(product)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
