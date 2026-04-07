from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models import db
from models.store import Store


class StoreRepository:
    def list_all_with_relations(self) -> List[Store]:
        stmt = (
            select(Store)
            .options(selectinload(Store.seller), selectinload(Store.categories))
            .order_by(Store.name)
        )
        return list(db.session.scalars(stmt).unique().all())

    def list_by_seller_id(self, seller_id: int) -> List[Store]:
        stmt = (
            select(Store)
            .where(Store.seller_id == seller_id)
            .options(selectinload(Store.seller), selectinload(Store.categories))
            .order_by(Store.name)
        )
        return list(db.session.scalars(stmt).unique().all())

    def get_by_id(self, store_id: int) -> Optional[Store]:
        stmt = (
            select(Store)
            .where(Store.id == store_id)
            .options(selectinload(Store.seller), selectinload(Store.categories))
        )
        return db.session.execute(stmt).scalar_one_or_none()

    def create(
        self,
        name: str,
        seller_id: int,
        is_active: bool,
        category_ids: List[int],
    ) -> Store:
        from models.category import Category

        s = Store(name=name, seller_id=seller_id, is_active=is_active)
        db.session.add(s)
        db.session.flush()
        for cid in category_ids:
            cat = db.session.get(Category, cid)
            if cat is not None:
                s.categories.append(cat)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return s

    def update(
        self,
        store: Store,
        name: str,
        seller_id: int,
        is_active: bool,
        category_ids: List[int],
    ) -> Store:
        from models.category import Category

        store.name = name
        store.seller_id = seller_id
        store.is_active = is_active
        store.categories.clear()
        for cid in category_ids:
            cat = db.session.get(Category, cid)
            if cat is not None:
                store.categories.append(cat)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return store

    def delete(self, store: Store) -> None:
        try:
            db.session.delete(store)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
